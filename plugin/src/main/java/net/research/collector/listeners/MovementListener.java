package net.research.collector.listeners;

import net.research.collector.*;
import org.bukkit.Location;
import org.bukkit.entity.Player;
import org.bukkit.event.*;
import org.bukkit.event.player.PlayerMoveEvent;
import org.bukkit.potion.PotionEffect;
import org.bukkit.potion.PotionEffectType;

public class MovementListener implements Listener {
    private final DataWriter writer;
    private final SessionManager sessions;

    public MovementListener(DataWriter writer, SessionManager sessions) {
        this.writer = writer;
        this.sessions = sessions;
    }

    @EventHandler(priority = EventPriority.MONITOR, ignoreCancelled = true)
    public void onMove(PlayerMoveEvent event) {
        long ts = System.currentTimeMillis();
        Player p = event.getPlayer();
        Location to = event.getTo();

        String sid = sessions.idOf(p);
        if (sid.equals("NONE")) return;

        int speedAmp = amplifier(p, PotionEffectType.SPEED);
        int jumpAmp = amplifier(p, PotionEffectType.JUMP);

        writer.write("movement.csv", String.format(
                "%d,%s,%s,%.5f,%.5f,%.5f,%.4f,%.4f,%b,%b,%b,%b,%d,%d,%d",
                ts, sid, p.getName(), to.getX(), to.getY(), to.getZ(), to.getYaw(), to.getPitch(),
                p.isOnGround(), p.isSprinting(), p.isSneaking(), p.getLocation().getBlock().isLiquid(),
                PingUtil.ping(p), speedAmp, jumpAmp
        ));
    }

    private int amplifier(Player p, PotionEffectType type) {
        for (PotionEffect e : p.getActivePotionEffects()) {
            if (e.getType().equals(type)) return e.getAmplifier() + 1;
        }
        return 0;
    }
}