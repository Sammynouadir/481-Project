import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

public class PTOControlSimulator {
    private JFrame frame;
    private JButton ptoButton, emergencyStopButton;
    private JPanel indicator, controlPanel, gearPanel, statusPanel;
    private JComboBox<String> gearShift;
    private JToggleButton lever;
    private JLabel statusLabel;
    private JTextArea logArea;

    public PTOControlSimulator() {
        frame = new JFrame("PTO Control Simulator");
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setSize(400, 450);
        frame.setLayout(new BorderLayout(10, 10));

        // Gear Shift Panel
        gearPanel = new JPanel(new FlowLayout(FlowLayout.CENTER, 10, 5));
        gearPanel.add(new JLabel("Gear:"));
        String[] gears = {"L", "N", "D", "R"};
        gearShift = new JComboBox<>(gears);
        gearPanel.add(gearShift);

        // PTO Control Panel
        controlPanel = new JPanel(new GridLayout(2, 2, 10, 10));
        ptoButton = new JButton("PTO Engage");
        ptoButton.setToolTipText("Engage/Disengage PTO");
        ptoButton.addActionListener(new PTOAction());

        lever = new JToggleButton("Lever (Push/Pull)");
        lever.setToolTipText("Push/Pull to control PTO");
        lever.addActionListener(new LeverAction());

        emergencyStopButton = new JButton("Emergency Stop");
        emergencyStopButton.setToolTipText("Instantly disengage PTO");
        emergencyStopButton.setForeground(Color.RED);
        emergencyStopButton.addActionListener(new EmergencyStopAction());

        controlPanel.add(ptoButton);
        controlPanel.add(lever);
        controlPanel.add(emergencyStopButton);

        // Indicator Light
        indicator = new JPanel();
        indicator.setPreferredSize(new Dimension(40, 40));
        indicator.setBackground(Color.GRAY);
        indicator.setBorder(BorderFactory.createLineBorder(Color.BLACK));

        JPanel indicatorPanel = new JPanel();
        indicatorPanel.add(new JLabel("PTO Indicator:"));
        indicatorPanel.add(indicator);

        // Status Panel
        statusPanel = new JPanel(new BorderLayout());
        statusLabel = new JLabel("Status: PTO Disengaged", SwingConstants.CENTER);
        statusPanel.add(statusLabel, BorderLayout.NORTH);

        // Log Area
        logArea = new JTextArea(5, 30);
        logArea.setEditable(false);
        JScrollPane scrollPane = new JScrollPane(logArea);
        statusPanel.add(scrollPane, BorderLayout.CENTER);

        // Assemble Frame
        frame.add(gearPanel, BorderLayout.NORTH);
        frame.add(controlPanel, BorderLayout.CENTER);
        frame.add(indicatorPanel, BorderLayout.WEST);
        frame.add(statusPanel, BorderLayout.SOUTH);

        frame.setVisible(true);
    }

    // PTO Button Action
    private class PTOAction implements ActionListener {
        @Override
        public void actionPerformed(ActionEvent e) {
            if (gearShift.getSelectedItem().equals("N")) {
                togglePTO();
            } else {
                showWarning("PTO can only be engaged in Neutral (N) gear.");
            }
        }
    }

    // Lever Action
    private class LeverAction implements ActionListener {
        @Override
        public void actionPerformed(ActionEvent e) {
            if (lever.isSelected()) {
                if (gearShift.getSelectedItem().equals("N")) {
                    engagePTO("Lever Engaged");
                } else {
                    lever.setSelected(false);
                    showWarning("PTO can only be engaged in Neutral (N) gear.");
                }
            } else {
                disengagePTO("Lever Disengaged");
            }
        }
    }

    // Emergency Stop Action
    private class EmergencyStopAction implements ActionListener {
        @Override
        public void actionPerformed(ActionEvent e) {
            disengagePTO("Emergency Stop Activated");
        }
    }

    // Toggle PTO State
    private void togglePTO() {
        if (indicator.getBackground() == Color.GREEN) {
            disengagePTO("PTO Disengaged");
        } else {
            engagePTO("PTO Engaged");
        }
    }

    // Engage PTO
    private void engagePTO(String message) {
        indicator.setBackground(Color.GREEN);
        updateStatus(message);
    }

    // Disengage PTO
    private void disengagePTO(String message) {
        indicator.setBackground(Color.GRAY);
        lever.setSelected(false);
        updateStatus(message);
    }

    // Update Status and Log
    private void updateStatus(String message) {
        statusLabel.setText("Status: " + message);
        logArea.append(message + "\n");
    }

    // Show Warning Message
    private void showWarning(String message) {
        JOptionPane.showMessageDialog(frame, message, "Warning", JOptionPane.WARNING_MESSAGE);
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(PTOControlSimulator::new);
    }
}
