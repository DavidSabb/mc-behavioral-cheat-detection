package net.research.collector;

import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.file.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicLong;

public class DataWriter {

    private final Path dir;
    private final BlockingQueue<String[]> queue = new LinkedBlockingQueue<>(200_000);
    private final AtomicLong dropped =  new AtomicLong();
    private volatile boolean running = true;
    private Thread worker;

    public DataWriter(Path dir) {
        this.dir = dir;
    }

    public void start() throws IOException {
        Files.createDirectories(dir);
        ensureHeader("movement.csv",
                "ts,session_id,player,x,y,z,yaw,pitch,on_ground,sprinting,sneaking,in_water,ping," +
                        "speed_amp,jump_amp");
        ensureHeader("combat.csv",
                "ts,session_id,attacker,target,ax,ay,az,ayaw,apitch,tx,ty,tz,reach,attacker_ping");
        ensureHeader("clicks.csv", "ts,session_id,player");
        ensureHeader("sessions.csv", "session_id,player,label,cheat_config,started_ts,ended_ts,notes");

        worker = new Thread(this::drain, "collector_writer");
        worker.setDaemon(true);
        worker.start();
    }

    private void ensureHeader(String file, String header) throws IOException {
        Path p = dir.resolve(file);
        if (!Files.exists(p)) {
            Files.write(p, (header + "\n").getBytes());
        }
    }

    public void write(String file, String csvLine) {
        if (!queue.offer(new String[]{file, csvLine})) {
            dropped.incrementAndGet();
        }
    }

    private void drain() {
        ConcurrentHashMap<String, BufferedWriter> writers = new ConcurrentHashMap<>();
        try {
            while (running || !queue.isEmpty()) {
                String[] item = queue.poll(500, TimeUnit.MILLISECONDS);
                if (item == null) {
                    for (BufferedWriter w : writers.values()) w.flush();
                    continue;
                }
                BufferedWriter w = writers.computeIfAbsent(item[0], f -> {
                    try {
                        return Files.newBufferedWriter(dir.resolve(f),
                                StandardOpenOption.CREATE, StandardOpenOption.APPEND);
                    } catch (IOException e) {
                        throw new RuntimeException(e);
                    }
                });
                w.write(item[1]);
                w.write('\n');
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        } catch (IOException e) {
            e.printStackTrace();
        } finally {
            for (BufferedWriter w : writers.values()) {
                try {
                    w.flush();
                    w.close();
                } catch (IOException ignored) {}
            }
        }
    }

    public long droppedCount() {
        return dropped.get();
    }

    public void stop() {
        running = false;
        try {
            if (worker != null) worker.join(5000);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}