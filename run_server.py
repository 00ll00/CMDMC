import subprocess
from threading import Thread
import re
import os
import signal

path='C:\\Users\\00ll00\\Desktop\\Server\\'
ops=['00ll00','LTCat']

def main():
    global Server,Shell,running
    running=True
    Server=subprocess.Popen(
        'java -jar '+path+'server.jar',
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=path
        )
    Shell=subprocess.Popen(
        'cmd',
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=path
        )
    Thread(target=read).start()
    Thread(target=write).start()
    Thread(target=shout).start()
    Thread(target=sherr).start()


def read():
    global running,Shell
    while running:
        line=Server.stdout.readline().decode('gbk').strip()
        if line:
            print(line)
            if re.match(r'\[([0-9]{2}:){2}[0-9]{2}\] \[Server thread/INFO\]: Stopping',line):
                running=False
            cmd = re.findall(r'\[(?:[0-9]{2}:){2}[0-9]{2}\] \[Server thread/INFO\]: <(.*)> ./(.*)',line)
            if cmd:
                op=cmd[0][0]
                cmd=cmd[0][1]
                if op in ops:
                    print('OP:'+op+'\nCMD:'+cmd)
                    if cmd=='^C':
                        Shell.kill()
                        Shell=subprocess.Popen(
                            'cmd',
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            cwd=path
                            )

                    else:
                        line=cmd+'\n'
                        Shell.stdin.write(line.encode())
                        Shell.stdin.flush()
                else:
                    line='tellraw @a {"text":"403 Forbidden","color":"red"}'+'\n'
                    Server.stdin.write(line.encode())
                    Server.stdin.flush()
            
    Server.stdout.close()
    exit()

def write():
    global running
    while running:
        line=input()+'\n'
        Server.stdin.write(line.encode())
        Server.stdin.flush()
        if line == 'stop':
            running=False
    Server.stdin.close()

def shout():
    global running
    while running:
        line=Shell.stdout.readline().decode('gbk').strip()
        if line:
            line='tellraw @a {"text":"'+line.replace('\\','\\\\').replace('"','\\"').replace('\'','\\\'')+'","color":"gray"}'+'\n'
            Server.stdin.write(line.encode())
            Server.stdin.flush()

def sherr():
    global running
    while running:
        line=Shell.stderr.readline().decode('gbk').strip()
        if line:
            line='tellraw @a {"text":"'+line.replace('\\','\\\\').replace('"','\\"').replace('\'','\\\'')+'","color":"dark_red"}'+'\n'
            Server.stdin.write(line.encode())
            Server.stdin.flush()


if __name__ == "__main__":
    main()