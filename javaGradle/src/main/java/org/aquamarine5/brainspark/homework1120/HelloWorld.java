package org.aquamarine5.brainspark.homework1120;

import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.WindowAdapter;
import java.awt.event.WindowEvent;

public class HelloWorld extends Frame {
    private final TextField textField;
    private final Button button;

    public HelloWorld() {
        super("HelloWorld");
        setLayout(new FlowLayout());
        textField = new TextField(20);
        button = new Button("Click Me");
        add(textField);
        add(button);
        button.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                textField.setText("HelloWorld");
            }
        });
        addWindowListener(new WindowAdapter() {
            @Override
            public void windowClosing(WindowEvent e) {
                dispose();
            }
        });
        setSize(300, 100);
    }

    public static void main(String[] args) {
        HelloWorld helloWorld = new HelloWorld();
        helloWorld.setVisible(true);
    }
}
