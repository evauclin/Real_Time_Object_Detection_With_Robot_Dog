import cv2
import sys
from PyQt5.QtCore import QTimer
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication
import doggydo.robot as robot
from doggydo.robot.client import Client
import threading
from doggydo.robot.thread import stop_thread
from doggydo.robot.command import COMMAND as cmd


class RobotHandler(QMainWindow):
    def __init__(self, ip: str):
        super(RobotHandler,self).__init__()
        self.client = robot.client.Client()
        self.client.move_speed = "8"
        self.IP = ip
        self._state = {
            "Relax": None,
        }

        # Timers
        self.timer=QTimer(self)
        self.timer.timeout.connect(self.refresh_image)

        self.timer_power = QTimer(self)
        self.timer_power.timeout.connect(self.power)

        self.timer_sonic = QTimer(self)
        self.timer_sonic.timeout.connect(self.getSonicData)

        self.initial=True

    def state(self, label):
        status = self._state.get(label)
        if status is None:
            raise RuntimeError("State is not initialized")
        return status

    def set_state(self, label, value):
        self._state[label] = value

    def start_video_capture(self):
        self.timer.start(10)

    def stop_video_capture(self):
        self.timer.stop()

    def closeEvent(self,event):
        try:
            self.timer_power.stop()
            self.timer.stop()
            stop_thread(self.video)
            stop_thread(self.instruction)
        except Exception as e:
            print(e)
        self.client.turn_off_client()
        print("close")

    def receive_instruction(self, ip):
        try:
            self.client.client_socket1.connect((ip, 5001))
            self.client.tcp_flag=True
            print ("Connecttion Successful !")
        except Exception as e:
            print ("Connect to server Faild!: Server IP is right? Server is opend?")
            self.client.tcp_flag=False
        while True:
            try:
                alldata=self.client.receive_data()
            except:
                self.client.tcp_flag=False
                break
            #print(alldata)
            if alldata=='':
                break
            else:
                cmdArray=alldata.split('\n')
                #print(cmdArray)
                if cmdArray[-1] !="":
                    cmdArray==cmdArray[:-1]
            for oneCmd in cmdArray:
                data=oneCmd.split("#")
                #print(data)
                if data=="":
                    self.client.tcp_flag=False
                    break
                elif data[0]==cmd.CMD_SONIC:
                    self.set_state("Sonic", data[1]+'cm')
                    #print('Obstacle:',data[1])
                elif data[0]==cmd.CMD_POWER:
                    if data[1]!="":
                        power_value=round((float(data[1]) - 7.00) / 1.40 * 100)
                        self.set_state("Power", power_value)
                elif data[0]==cmd.CMD_RELAX:
                    if data[1]=="0":
                        self.set_state("Relax", "Relax")
                    else:
                        self.set_state("Relax", "Too tired...")

    def refresh_image(self):
        try:
            if self.client.video_flag == False:
                height, width, bytesPerComponent=self.client.image.shape
                #print (height, width, bytesPerComponent)
                cv2.cvtColor(self.client.image, cv2.COLOR_BGR2RGB, self.client.image)
                self.client.video_flag = True
        except Exception as e:
            print(e)

    def connect(self):
        self.client.turn_on_client(self.IP)
        self.video=threading.Thread(target=self.client.receiving_video,args=(self.IP,))
        self.instruction=threading.Thread(target=self.receive_instruction,args=(self.IP,))
        self.video.start()
        self.instruction.start()
        self.timer_power.start(1000)

    def disconnect(self):
        try:
            stop_thread(self.video)
        except:
            pass
        try:
            stop_thread(self.instruction)
        except:
            pass
        self.client.tcp_flag=False
        self.client.turn_off_client()
        self.timer_power.stop()

    def stand(self):
        self.initial=False
        #self.drawpoint = [585, 135]
        self.state("roll", 0)
        self.state("pitch", 0)
        self.state("yaw", 0)
        self.attitude()
        time.sleep(0.2)
        self.state("horizon", 0)
        self.horizon()
        time.sleep(0.1)
        self.initial = True

    def stop(self):
        command=cmd.CMD_MOVE_STOP+"#"+self.move_speed+'\n'
        self.client.send_data(command)
        #print (command)

    def forward(self):
        self.stand()
        command=cmd.CMD_MOVE_FORWARD+"#"+self.move_speed+'\n'
        self.client.send_data(command)
        #print (command)

    def backward(self):
        self.stand()
        command=cmd.CMD_MOVE_BACKWARD+"#"+self.move_speed+'\n'
        self.client.send_data(command)
        #print (command)

    def step_left(self):
        self.stand()
        command=cmd.CMD_MOVE_LEFT+"#"+self.move_speed+'\n'
        self.client.send_data(command)
        #print (command)

    def step_right(self):
        self.stand()
        command=cmd.CMD_MOVE_RIGHT+"#"+self.move_speed+'\n'
        self.client.send_data(command)
        #print (command)

    def left(self):
        self.stand()
        command=cmd.CMD_TURN_LEFT+"#"+self.move_speed+'\n'
        self.client.send_data(command)
        #print (command)

    def right(self):
        self.stand()
        command=cmd.CMD_TURN_RIGHT+"#"+self.move_speed+'\n'
        self.client.send_data(command)
        #print (command)

    def relax(self):
        if self.state("Relax") == 'Relax':
            command=cmd.CMD_RELAX+'\n'
            self.client.send_data(command)
            #print (command)
        else:
            pass

    def buzzer(self):
        if self.state('Buzzer') == 'Buzzer':
            command=cmd.CMD_BUZZER+'#1'+'\n'
            self.client.send_data(command)
            self.set_state('Buzzer', 'Noise')
            #print (command)
        else:
            command=cmd.CMD_BUZZER+'#0'+'\n'
            self.client.send_data(command)
            self.set_state('Buzzer', 'Buzzer')
            #print (command)

    def sonic(self):
        if self.state('Sonic') == 'Sonic':
            self.timer_sonic.start(100)
            self.set_state('Sonic', 'Close')

        else:
            self.timer_sonic.stop()
            self.set_state('Sonic', 'Sonic')

    def getSonicData(self):
        command=cmd.CMD_SONIC+'\n'
        self.client.send_data(command)
        #print (command)

    def height(self):
        try:
            hei=str(self.state("height"))
            command=cmd.CMD_HEIGHT+"#"+hei+'\n'
            self.client.send_data(command)
            #print(command)
        except Exception as e:
            print(e)

    def horizon(self):
        try:
            hor=str(self.state("horizon"))
            command=cmd.CMD_HORIZON+"#"+hor+'\n'
            if self.initial:
                self.client.send_data(command)
            #print(command)
        except Exception as e:
            print(e)

    def head(self):
        try:
            angle=str(self.state("head"))
            self.set_state("head", angle)
            command=cmd.CMD_HEAD+"#"+angle+'\n'
            self.client.send_data(command)
            #print(command)
        except Exception as e:
            print(e)

    def power(self):
        try:
            command=f"{cmd.CMD_POWER}\n"
            self.client.send_data(command)
            #print (command)
            command = "CMD_WORKING_TIME\n"
            self.client.send_data(command)
        except Exception as e:
            print(e)

    def attitude(self):
        try:
            r=str(self.state("roll"))
            p=str(self.state("pitch"))
            y=str(self.state("yaw"))
            command = cmd.CMD_ATTITUDE + '#' + r + '#' + p + '#' + y + '\n'
            if self.initial:
                self.client.send_data(command)
        except Exception as e:
            print(e)


def main(ip):
    app = QApplication(sys.argv)
    handle = RobotHandler(ip)
    handle.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main(sys.argv[1])
