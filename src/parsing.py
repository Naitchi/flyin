#from pydantic import Field, BaseModel


class Parser():
    def run_trough_file(content: str):
        for line in content.split('\n'):
            if len(line) < 1 or line[0] == '#':
                continue
            for word in line.split(' '):
                print("word ", word)
            print("line: ", line)
