package net.research.collector.listeners;

import net.research.collector.*;
import org.bukkit.entity.Player;
import org.bukkit.event.*;
import org.bukkit.event.player.PlayerAnimationEvent;
import org.bukkit.event.player.PlayerAnimationType;

public class ClickListener implements Listener {
    private final DataWriter writer;
    private final SessionManager sessions;

    public ClickListener(DataWriter writer, SessionManager sessions) {
        this.writer = writer;
        this.sessions = sessions;
    }

    @EventHandler(priority = EventPriority.MONITOR, ignoreCancelled = true)
    public void onSwing(PlayerAnimationEvent event) {
        long ts = System.currentTimeMillis();
        if (event.getAnimationType() != PlayerAnimationType.ARM_SWING) return;

        Player p = event.getPlayer();
        String sid = sessions.idOf(p);

        if (sid.equals("NONE")) return;

        writer.write("clicks.csv", ts + "," + sid + "," + p.getName());
    }
}