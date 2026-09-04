package net.research.collector;

import org.bukkit.entity.Player;
import java.util.*;

public class SessionManager {
    public static class Session {
        public final String id = UUID.randomUUID().toString().substring(0,8);
        public final String player;
        public final long started = System.currentTimeMillis();
        public String label = "UNLABELED";
        public String config = "";

        Session(String player) {
            this.player = player;
        }
    }

    private final Map<UUID, Session> active = new HashMap<>();

    public Session open(Player p) {
        Session s = new Session(p.getName());
        active.put(p.getUniqueId(), s);
        return s;
    }

    public Session get(Player p) {
        return active.get(p.getUniqueId());
    }

    public String idOf(Player p) {
        Session s = active.get(p.getUniqueId());
        return s == null ? "NONE" : s.id;
    }

    public Session close(Player p) {
        return active.remove(p.getUniqueId());
    }
}