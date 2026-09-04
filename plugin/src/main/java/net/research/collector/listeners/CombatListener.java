package net.research.collector.listeners;

import net.research.collector.*;
import org.bukkit.Location;
import org.bukkit.entity.Player;
import org.bukkit.event.*;
import org.bukkit.event.entity.EntityDamageByEntityEvent;

public class CombatListener implements Listener {
    private final DataWriter writer;
    private final SessionManager sessions;

    public CombatListener(DataWriter writer, SessionManager sessions) {
        this.writer = writer;
        this.sessions = sessions;
    }

    @EventHandler(priority = EventPriority.MONITOR, ignoreCancelled = true)
    public void onHit(EntityDamageByEntityEvent event) {
        long ts = System.currentTimeMillis();

        if (!(event.getDamager() instanceof Player)) return;
        if (!(event.getEntity() instanceof Player)) return;

        Player attacker = (Player) event.getDamager();
        Player target = (Player) event.getEntity();

        String sid = sessions.idOf(attacker);
        if (sid.equals("NONE")) return;

        Location eye = attacker.getEyeLocation();
        Location tgt = target.getLocation();

        double reach = horizontalHitBoxDistance(eye, tgt);
    }

    private double horizontalHitBoxDistance(Location eye, Location target) {
        double halfWidth = 0.3;
        double height = 1.8;

        double dx = Math.max(0, Math.abs(eye.getX() - target.getX()) - halfWidth);
        double dz = Math.max(0, Math.abs(eye.getZ() - target.getZ()) - halfWidth);

        double eyeY = eye.getY();
        double minY = target.getY();
        double maxY = target.getY() + height;
        double dy = eyeY < minY ? minY - eyeY : (eyeY > maxY ? eyeY - maxY : 0);

        return Math.sqrt(dx * dx + dy * dy + dz * dz);
    }
}