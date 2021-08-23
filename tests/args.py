import subprocess
import sys

def get_index(itterable, index):
    if index in range(len(itterable)):
        return itterable[index]

if __name__ == '__main__':
    
    print(sys.argv)
    
    if len(sys.argv) == 1:
        
        subprocess.Popen(['python', sys.argv[0], 'test'])



