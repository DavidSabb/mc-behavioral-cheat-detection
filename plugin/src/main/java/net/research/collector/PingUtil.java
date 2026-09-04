package net.research.collector;

import org.bukkit.entity.Player;
import java.lang.reflect.Field;
import java.lang.reflect.Method;

public final class PingUtil {
    private static Method getHandle;
    private static Field pingField;
    private static boolean broken = false;

    public static int ping(Player player) {
        if (broken) return -1;
        try {
            if (getHandle== null) {
                getHandle = player.getClass().getMethod("getHandle");
            }
            Object handle = getHandle.invoke(player);
            if(pingField == null) {
                pingField = handle.getClass().getField("ping");
            }
            return pingField.getInt(handle);
        } catch (Exception e) {
            broken = true;
            return -1;
        }
    }
}