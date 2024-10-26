import sys
import boto3
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QMessageBox
from IaC.launch_instance import instance_id


class EC2Manager(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set up the AWS EC2 client
        self.ec2 = boto3.client('ec2', region_name='eu-west-3')
        self.instance_id = instance_id

        # Initialize UI components
        self.start_button = QPushButton("Start Instance")
        self.stop_button = QPushButton("Stop Instance")
        self.status_button = QPushButton("Get Status")
        self.status_label = QLabel("Instance Status: Unknown")

        # Set up the UI layout and signals
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("AWS EC2 Manager")
        self.setGeometry(100, 100, 300, 200)

        # noinspection PyUnresolvedReferences
        self.start_button.clicked.connect(self.start_instance)
        # noinspection PyUnresolvedReferences
        self.stop_button.clicked.connect(self.stop_instance)
        # noinspection PyUnresolvedReferences
        self.status_button.clicked.connect(self.get_instance_status)

        # Layout setup
        layout = QVBoxLayout()
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.status_button)
        layout.addWidget(self.status_label)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def start_instance(self):
        try:
            self.ec2.start_instances(InstanceIds=[self.instance_id])
            QMessageBox.information(self, "Success", "Instance starting...")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start instance: {e}")

    def stop_instance(self):
        try:
            self.ec2.stop_instances(InstanceIds=[self.instance_id])
            QMessageBox.information(self, "Success", "Instance stopping...")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to stop instance: {e}")

    def get_instance_status(self):
        try:
            response = self.ec2.describe_instances(InstanceIds=[self.instance_id])
            state = response['Reservations'][0]['Instances'][0]['State']['Name']
            self.status_label.setText(f"Instance Status: {state}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to get instance status: {e}")


# Main application execution
def main():
    app = QApplication(sys.argv)
    manager = EC2Manager()
    manager.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()