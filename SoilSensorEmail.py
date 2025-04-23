import RPi.GPIO as GPIO
import time
import smtplib
from email.message import EmailMessage
from datetime import datetime
import pytz

# Sensor Configuration
SENSOR_PIN = 14
GPIO.setmode(GPIO.BCM)
GPIO.setup(SENSOR_PIN, GPIO.IN)

# Email Settings
FROM_EMAIL = "2714877989@qq.com"
FROM_PASSWORD = "zvjiwfbwfxeodfac"
TO_EMAIL = "859622520@qq.com"

# Timezone Settings
TIMEZONE = pytz.timezone('Asia/Shanghai')

# Scheduled Report Times (24-hour format)
REPORT_TIMES = [8,12,16,20]

class PlantMonitor:
    def __init__(self):
        self.last_report_hour = None
        self.shutdown = False
        
    def get_current_time(self):
        """Get current time object"""
        return datetime.now(TIMEZONE)
    
    def send_email(self, subject, body):
        """Send email notification"""
        try:
            msg = EmailMessage()
            msg.set_content(body)
            msg['From'] = FROM_EMAIL
            msg['To'] = TO_EMAIL
            msg['Subject'] = subject

            with smtplib.SMTP_SSL('smtp.qq.com', 465) as server:
                server.login(FROM_EMAIL, FROM_PASSWORD)
                server.send_message(msg)
            
            print("Email sent successfully")
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False
    
    def check_sensor(self):
        """Check sensor status"""
        return GPIO.input(SENSOR_PIN)  # 0=dry, 1=wet
    
    def should_send_report(self, current_hour):
        """Check if it's time to send report"""
        # Current hour is in scheduled times and we haven't sent for this hour
        return current_hour in REPORT_TIMES and self.last_report_hour != current_hour
    
    def run(self):
        """Main operation loop"""
        print("Plant moisture monitoring system starting...")
        print(f"Scheduled report times: {', '.join(str(t) for t in REPORT_TIMES)}:00")
        
        try:
            while not self.shutdown:
                now = self.get_current_time()
                current_hour = now.hour
                
                if self.should_send_report(current_hour):
                    sensor_state = self.check_sensor()
                    status = "Wet" if sensor_state else "Dry"
                    
                    report_time = now.strftime("%Y-%m-%d %H:%M:%S")
                    subject = f"Plant Status Report {report_time}"
                    body = f"""Plant Status Monitoring Report:
                    
                    Report Time: {report_time}
                    Current Status: {status}
                    
                    Recommended Action: {'No watering needed' if sensor_state else 'Please water the plant!'}
                    """
                    
                    if self.send_email(subject, body):
                        self.last_report_hour = current_hour
                        print(f"{report_time} - Status report sent")
                
                time.sleep(60)  # Check time every minute
        
        except KeyboardInterrupt:
            print("Interrupt signal received, preparing to exit...")
        finally:
            GPIO.cleanup()
            print("System safely shut down")

if __name__ == "__main__":
    monitor = PlantMonitor()
    monitor.run()

