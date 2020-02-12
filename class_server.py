# -*- coding: utf-8 -*-
"""
Created on Tue Jan 28 22:37:29 2020

@author: rlgns
"""

import socket
from matplotlib import pyplot as plt
import numpy as np 
import cv2
#from scipy.spatial import distance_matrix
from scipy.spatial import distance




class TCP_server():
    def __init__(self, HOST= '127.0.0.1', PORT= 45545):
        
        
        # 손바닥 가운데 위치 변위에 관한 정보
        self.pre_left = 0
        self.pre_right = 0
        self.pre_up = 0
        self.pre_down = 0
        self.x_differ = 0
        self.y_differ = 0
        
        # ip 및 port number
        self.HOST = HOST
        self.PORT = PORT
        # 소켓 객체를 생성합니다. 
        # 주소 체계(address family)로 IPv4, 소켓 타입으로 TCP 사용합니다.  
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # 포트 사용중이라 연결할 수 없다는 
        # WinError 10048 에러 해결를 위해 필요합니다. 
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # bind 함수는 소켓을 특정 네트워크 인터페이스와 포트 번호에 연결하는데 사용됩니다.
        # HOST는 hostname, ip address, 빈 문자열 ""이 될 수 있습니다.
        # 빈 문자열이면 모든 네트워크 인터페이스로부터의 접속을 허용합니다. 
        # PORT는 1-65535 사이의 숫자를 사용할 수 있습니다.  
        self.server_socket.bind((self.HOST, self.PORT))
        
        # 서버가 클라이언트의 접속을 허용하도록 합니다. 
        self.server_socket.listen()#TCP
        
        self.client_socket, self.addr = self.server_socket.accept() #TCP
        
        # 접속한 클라이언트의 주소입니다.
        print('Connected by', self.addr)# TCP
        
        self.image = plt.figure() # 관절이미지를 위한 창 생성 
        
        
    def activate_network(self):
        #while True:
    
    
            # 클라이언트가 보낸 메시지를 수신하기 위해 대기합니다. 
        self.data = self.client_socket.recv(1024) # TCP
            #data, addr = server_socket.recvfrom(1024)
    
            # 빈 문자열을 수신하면 루프를 중지합니다. 
        if not self.data:
            print("close the connection")
            self.close_server()

            # 수신받은 문자열을 출력합니다.
            #print('Received from', addr, data.decode())
            
        x_points , y_points = self.split_x_y(self.data)
        
        return self.draw_hand(x_points,y_points), x_points, y_points
            
            # 받은 문자열을 다시 클라이언트로 전송해줍니다.(에코) 
            #client_socket.send(data)
        #self.close_server()
        
    def close_server(self):
        # 소켓을 닫습니다.
        print("close the connection")
        self.client_socket.close() # TCP
        self.server_socket.close()
        
    def split_x_y(self, jointdata):
        try:
            data = jointdata.decode().split(",")
            data.pop() # remove '\n'
            x_points = [int(x) for idx, x in enumerate(data) if idx%2 == 0]
            y_points = [int(y) for idx, y in enumerate(data) if idx%2 == 1]
            return x_points, y_points
        except ValueError:
            return None,None
            pass
        except AttributeError:
            return None,None
            pass
        
    def jointdata_preprocessing(self, x_points, y_points):
    #관절 정보를 받아 적절한 인풋으로 변환
        try:
            #손 목과 손 중앙 정보 추출 for nomalize 
            # 4를 곱해줘서 다른 거리정보가 0~1 사이로 맵핑이 되도록 조정 
            normalize_info = 4 * distance.euclidean([x_points[0],y_points[0]], [x_points[1],y_points[1]])
            
            
            #1 or 2 손바닥 6 엄지 10 검지 14 중지 18약지 22새끼
            # 손바닥과 손가락간의 거리
            input_data1 = [distance.euclidean([x_points[0],y_points[0]], [x_points[i],y_points[i]])/normalize_info for i in [5, 9, 13, 17, 21]]
            # 엄지과 나머지 손가락간의 거리
            input_data2 = [distance.euclidean([x_points[5],y_points[5]], [x_points[i],y_points[i]])/normalize_info for i in [9, 13, 17, 21]]
            # 검지과 나머지 손가락간의 거리
            input_data3 = [distance.euclidean([x_points[9],y_points[9]], [x_points[i],y_points[i]])/normalize_info for i in [13, 17, 21]]
            # 중지과 나머지 손가락간의 거리
            input_data4 = [distance.euclidean([x_points[13],y_points[13]], [x_points[i],y_points[i]])/normalize_info for i in [17, 21]]
            # 약지- 새
            input_data5 = [distance.euclidean([x_points[17],y_points[17]], [x_points[21],y_points[21]])/normalize_info]
            
            # 손바닥 가운데 위치 변위에 관한 정보
            
            # 이전 프레임의 정보와 비교 
            self.x_differ = self.x_differ - x_points[1]
            self.y_differ = self.y_differ - y_points[1]
            
            if self.x_differ > 0 :
                self.pre_left += self.x_differ
            else:
                self.pre_right -=self.x_differ
            if self.y_differ > 0 :
                self.pre_down += self.y_differ
            else:
                self.pre_up -= self.y_differ
                            
            # 현재 프레임의 정보를 이전 프레임 정보로 pass
            self.x_differ = x_points[1]
            self.y_differ = y_points[1]
            
            dir_info = [self.pre_up, self.pre_down, self.pre_right, self.pre_left]
            
            return input_data1+input_data2+input_data3+input_data4+input_data5 # 총 15개의 성분 list + 4개의 방향 변
        except ValueError:
            pass
        except AttributeError:
            pass
        except TypeError:
            pass
    
    def draw_hand(self, x_points, y_points):
    # 관절정보를 토대로 손 형태를 그려서 화면에 출력
    
    #plt 이미지는 주피터에서만 자동으로 뜨는건가?
    #실시간으로 들어오는 영상에대한 처리 아직 안됨 왜 커널 죽음(응답없음)
    
        plt.cla()
        plt.clf()
        try:
            
            plt.ylim(0, 480)
            plt.xlim(0, 640)
            plt.scatter(x_points,y_points)
            
            plt.plot(x_points[2:6], y_points[2:6])
            
            plt.plot(x_points[6:10], y_points[6:10])
            
            plt.plot(x_points[10:14], y_points[10:14])
            plt.plot(x_points[14:18], y_points[14:18])
            plt.plot(x_points[18:22], y_points[18:22])
            ax = self.image.gca()
            ax.axis('off')
            self.image.canvas.draw()
            cv_image = np.array(self.image.canvas.renderer._renderer)
            cv_image = np.flip(cv_image, 0)
            cv_image = np.flip(cv_image, 1)
            self.cv_image = cv_image
            #cv2.imshow('image',cv_image)
            #cv2.waitKey(33)
            return self.cv_image
            
        except ValueError:
            return self.cv_image
            pass
        except AttributeError:
            return self.cv_image
            pass
        except TypeError:
            return self.cv_image
            pass
    
    def get_data(self):
        return self.data
        

if __name__ == "__main__":
    # 접속할 서버 주소입니다. 여기에서는 루프백(loopback) 인터페이스 주소 즉 localhost를 사용합니다. 

    HOST = '127.0.0.1'

    # 클라이언트 접속을 대기하는 포트 번호입니다.   
    PORT = 45545
    
    server = TCP_server(HOST, PORT)
    
    server.activate_network()
    
    
    
        