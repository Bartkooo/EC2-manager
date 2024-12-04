import sys
from datetime import datetime, timedelta, timezone
import boto3
import json
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QMessageBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.dates import DateFormatter, MinuteLocator


class EC2Manager(QMainWindow):
    def __init__(self):
        super().__init__()

        # Load the instance ID from file
        self.instance_id = self.load_instance_id()

        # Set up the AWS EC2 client
        self.ec2 = boto3.client('ec2', region_name='eu-west-3')
        self.cloudwatch = boto3.client('cloudwatch', region_name='eu-west-3')

        # Initialize UI components
        self.start_button = QPushButton("Start Instance")
        self.stop_button = QPushButton("Stop Instance")
        self.reboot_button = QPushButton("Reboot Instance")
        self.status_button = QPushButton("Get Status")
        self.metrics_button = QPushButton("Get Metrics")
        self.status_label = QLabel("Instance Status: N/A")
        self.cpu_label = QLabel("CPU Usage: N/A")
        self.memory_label = QLabel("Memory Usage: N/A")

        # Initialize the graph
        self.cpu_graph = CPUUsageGraph()

        # Set up the UI layout and signals
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("AWS EC2 Manager")
        self.setGeometry(100, 100, 600, 600)

        # noinspection PyUnresolvedReferences
        self.start_button.clicked.connect(self.start_instance)
        # noinspection PyUnresolvedReferences
        self.stop_button.clicked.connect(self.stop_instance)
        # noinspection PyUnresolvedReferences
        self.reboot_button.clicked.connect(self.reboot_instance)
        # noinspection PyUnresolvedReferences
        self.status_button.clicked.connect(self.get_instance_status)
        # noinspection PyUnresolvedReferences
        self.metrics_button.clicked.connect(self.get_instance_metrics)

        # Layout setup
        layout = QVBoxLayout()
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.reboot_button)
        layout.addWidget(self.status_button)
        layout.addWidget(self.metrics_button)
        layout.addWidget(self.status_label)
        layout.addWidget(self.cpu_label)
        layout.addWidget(self.memory_label)
        layout.addWidget(self.cpu_graph)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def load_instance_id(self):
        try:
            with open('instance_id.json', 'r') as f:
                data = json.load(f)
                return data['instance_id']
        except FileNotFoundError:
            QMessageBox.critical(self, "Error", "Instance ID file not found. Please run 'launch_instance.py' first.")
            sys.exit(1)
        except KeyError:
            QMessageBox.critical(self, "Error", "Invalid instance ID file format.")
            sys.exit(1)

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

    def reboot_instance(self):
        try:
            self.ec2.reboot_instances(InstanceIds=[self.instance_id])
            QMessageBox.information(self, "Success", "Rebooting instance...")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to reboot instance: {e}")

    def get_instance_status(self):
        try:
            response = self.ec2.describe_instances(InstanceIds=[self.instance_id])
            state = response['Reservations'][0]['Instances'][0]['State']['Name']
            self.status_label.setText(f"Instance Status: {state.capitalize()}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to get instance status: {e}")

    def get_instance_metrics(self):
        try:
            # Retrieve CPU usage
            cpu_response = self.cloudwatch.get_metric_statistics(
                Namespace='AWS/EC2',
                MetricName='CPUUtilization',
                Dimensions=[{'Name': 'InstanceId', 'Value': self.instance_id}],
                StartTime=datetime.now(timezone.utc) - timedelta(minutes=30),
                EndTime=datetime.now(timezone.utc),
                Period=300,
                Statistics=['Average']
            )
            cpu_usage = cpu_response['Datapoints'][0]['Average'] if cpu_response['Datapoints'] else "N/A"

            # Retrieve memory usage
            mem_response = self.cloudwatch.get_metric_statistics(
                Namespace='CWAgent',
                MetricName='mem_used_percent',
                Dimensions=[{'Name': 'InstanceId', 'Value': self.instance_id}],
                StartTime=datetime.now(timezone.utc) - timedelta(minutes=15),
                EndTime=datetime.now(timezone.utc),
                Period=300,
                Statistics=['Average']
            )
            mem_usage = mem_response['Datapoints'][0]['Average'] if mem_response['Datapoints'] else "N/A"

            timestamps = [dp['Timestamp'] for dp in cpu_response['Datapoints']]
            cpu_usages = [dp['Average'] for dp in cpu_response['Datapoints']]
            timestamps, cpu_usages = zip(*sorted(zip(timestamps, cpu_usages)))

            # Update metrics labels
            self.cpu_label.setText(f"CPU Usage: {round(cpu_usage, 2)}%")

            # In case of a problem with loading memory usage, the application will continue to work
            self.memory_label.setText(f"Memory Usage: "
                                      f"{round(float(mem_usage), 2) if mem_usage != "N/A" else mem_usage}%")

            self.cpu_graph.update_graph(timestamps, cpu_usages)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to retrieve metrics: {e}")


class CPUUsageGraph(FigureCanvas):
    def __init__(self):
        self.figure = Figure()
        self.ax = self.figure.add_subplot(111)
        super().__init__(self.figure)

        # Initial plot settings
        self.ax.set_title("CPU Usage Over Time")
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("CPU Usage (%)")
        self.ax.grid(True)

    def update_graph(self, timestamps, cpu_usages):
        self.ax.clear()
        self.ax.plot(timestamps, cpu_usages, marker='o', linestyle='-', color='b')

        # Change date format
        self.ax.xaxis.set_major_formatter(DateFormatter('%H:%M'))
        self.ax.xaxis.set_major_locator(MinuteLocator(interval=5))
        self.ax.set_xlim([min(timestamps), max(timestamps)])

        self.ax.set_title("CPU Usage Over Time")
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("CPU Usage (%)")
        self.figure.autofmt_xdate()
        self.draw()


def main():
    app = QApplication(sys.argv)
    manager = EC2Manager()
    manager.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
