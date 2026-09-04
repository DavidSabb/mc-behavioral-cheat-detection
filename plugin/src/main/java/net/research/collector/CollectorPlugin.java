package net.research.collector;

import net.research.collector.listeners.*;
import org.bukkit.ChatColor;
import org.bukkit.command.*;
import org.bukkit.entity.Player;
import org.bukkit.event.*;
import org.bukkit.event.player.*;
import org.bukkit.plugin.java.JavaPlugin;

import java.io.IOException;

public class CollectorPlugin extends JavaPlugin implements Listener {
    private DataWriter writer;
    private SessionManager sessions;

    @Override
    public void onEnable() {
        writer = new DataWriter(getDataFolder().toPath());
        try {
            writer.start();
        } catch (IOException e) {
            getLogger().severe("Could not start writer: " + e.getMessage());
            getServer().getPluginManager().disablePlugin(this);
            return;
        }

        sessions = new SessionManager();

        getServer().getPluginManager().registerEvents(this, this);
        getServer().getPluginManager().registerEvents(
                new MovementListener(writer, sessions), this);
        getServer().getPluginManager().registerEvents(
                new CombatListener(writer, sessions), this);
        getServer().getPluginManager().registerEvents(
                new ClickListener(writer, sessions), this);

        getLogger().info("Collector enabled");
    }

    @Override
    public void onDisable() {
        if (writer != null) {
            long dropped = writer.droppedCount();
            if (dropped > 0) {
                getLogger().warning("DROPPED " + dropped + " RECORDS - data is incomplete!");
            }
            writer.stop();
        }
    }

    @EventHandler
    public void onJoin(PlayerJoinEvent e) {
        SessionManager.Session s = sessions.open(e.getPlayer());
        e.getPlayer().sendMessage(ChatColor.YELLOW + "Session " + s.id + " open. Set a label with /session" +
                " <label> before playing");
    }

    @EventHandler
    public void onQuit(PlayerQuitEvent e) {
        SessionManager.Session s = sessions.close(e.getPlayer());
        if (s == null) return;
        writer.write("sessions.csv", String.format("%s,%s,%s,%s,%d,%d",
                s.id,s.player,s.label,s.config,s.started,System.currentTimeMillis()));
        if (s.label.equals("UNLABELLED")) {
            getLogger().warning("Session " + s.id + " ended UNLABELED - discard this data");
        }
    }
    @Override
    public boolean onCommand(CommandSender sender, Command cmd, String lbl, String[] args) {
        if (!(sender instanceof Player)) return true;
        Player p = (Player) sender;
        SessionManager.Session s = sessions.get(p);
        if (s == null) { p.sendMessage(ChatColor.RED + "No active session."); return true; }

        if (args.length == 0 || args[0].equalsIgnoreCase("status")) {
            p.sendMessage(ChatColor.AQUA + "Session " + s.id
                    + " | label=" + s.label + " | config=" + s.config);
            return true;
        }

        s.label = args[0].toUpperCase();
        if (args.length > 1) {
            StringBuilder sb = new StringBuilder();
            for (int i = 1; i < args.length; i++) sb.append(args[i]).append(' ');
            s.config = sb.toString().trim().replace(',', ';');
        }
        p.sendMessage(ChatColor.GREEN + "Labelled as " + s.label
                + (s.config.isEmpty() ? "" : " (" + s.config + ")"));
        return true;
    }
}