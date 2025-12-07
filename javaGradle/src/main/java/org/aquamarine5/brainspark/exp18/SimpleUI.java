package org.aquamarine5.brainspark.exp18;

import java.awt.*;
import java.awt.event.WindowAdapter;
import java.awt.event.WindowEvent;

public class SimpleUI extends Frame {
    public SimpleUI() {
        super("Hello World Frame");
        Label label = new Label("Hello World");
        add(label);
        setSize(300, 200);
        addWindowListener(new WindowAdapter() {
            public void windowClosing(WindowEvent we) {
                System.exit(0);
            }
        });
    }

    public static void main(String[] args) {
        SimpleUI frame = new SimpleUI();
        frame.setVisible(true);
    }
}
