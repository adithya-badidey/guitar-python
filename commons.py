import re

notes = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
ntoi = {value:index for index, value in enumerate(notes)}
iton = {index:value for index, value in enumerate(notes)}

note_splitter = re.compile("([a-zA-z#]+)([0-9]+)")
class Note:
    def __init__(self, note):
        if isinstance(note, str):
            finds = note_splitter.findall(note)
            self.n =  int(finds[0][1]) * len(notes) + ntoi[finds[0][0]]
            # print(self.n)
        elif isinstance(note, int):
            self.n = note
    
    def __add__(self, i):
        return Note(self.n + i)

    def __sub__(self, i):
        return Note(self.n - i)

    def __str__(self):
        o = self.n // len(notes)
        note = self.n % len(notes)
        return f"{iton[note]}{o}"

    def getRootNoteIndex(self):
        if self.n < 0:
            raise Exception("n cant be less than 0")
        
        return self.n % len(notes)
    
    def getRootNote(self):
        return notes[self.n % len(notes)]

class Guitar:
    def __init__(self, num_frets=20, tuning=['E2','A2','D3','G3','B3','E4']):
        self.num_frets = num_frets
        self.tuning = [Note(i) for i in tuning]

    def getNoteIfIn(self, i, noteset):
      if (not noteset) or (i in noteset):
        if noteset and i.getRootNoteIndex() == noteset.getRootNoteIndex():
          return f"({i.getRootNote()})"
        else:
          return f" {i.getRootNote()} "
      return f"   "
        
    def printFretboardDiagram(self, noteset=None):
        for i in self.tuning[::-1]:
            print(f"{self.getNoteIfIn(i, noteset):<4}█",end="")
            for j in range(1, self.num_frets):
                print(f"{self.getNoteIfIn((i+j), noteset):<5}|",end="")
            print()
        # print(f"   ┖",end="")
        # for j in range(1, self.num_frets):
        #     print(f"──────┴",end="")
        # print()
        print(f"    ",end="")
        for i in range(1, self.num_frets):
            if i in [5, 7, 9, 15, 17, 19, 21]:
                print(f"  •  ",end=" ")
            elif i == 12:
                print(f"  •• ",end=" ")
            else:
                print(f"     ",end=" ")
        print()

class NoteSet:
    def __init__(self, progression, root=None):
      if root is not None:
        self.root = root.getRootNoteIndex()
        self.prog = [(self.root + p)%len(notes) for p in progression]
      else:
        self.prog = progression
        self.root = self.prog[0]

    def __str__(self):
        return " ".join([iton[i] for i in self.prog])

    def __contains__(self, x):
      if isinstance(x, Note):
        return x.getRootNoteIndex() in self.prog
      elif isinstance(x, NoteSet):
        return sum(1 for i in x.prog if i in self.prog) == len(x.prog)

    def getRootNoteIndex(self):
        return self.root

def changeRootNote(noteset, index):
  if index > len(noteset.prog) or index < 0:
    raise Exception("Invalid Index to change root note")
  if index == 0:
    return NoteSet(noteset.prog)

  newProg = noteset.prog[index:] + noteset.prog[:index]
  return NoteSet(newProg)
  

chords = {
  'maj':  [0,4,7],
  'maj6': [0,4,7,6],
  'dom7': [0,4,7,10],
  'maj7': [0,4,7,11],
  'aug':  [0,4,8],
  'aug7': [0,4,8,10],
  'min':  [0,3,7],
  'min6': [0,3,7,9],
  'min7': [0,3,7,10],
  'minmaj7': [0,3,7,11],
  'dim':     [0,3,6],
  'dim7':    [0,3,6,9],
  'hdim7':   [0,3,6,10],
}