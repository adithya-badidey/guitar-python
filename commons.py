import re

notes = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
flats = ['C','Db','D','Eb','E','F','Gb','G','Ab','A','Bb','B']
ntoi = {value:index for index, value in enumerate(notes)}
for index, value in enumerate(flats):
  ntoi[value] = index
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
        else:
            raise Exception(f"Unknown dtype for note: {type(note)}")
    
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
    """
    A noteset is a particular set of notes. Unlike a scale, 
    its supposed to be very specific to the particular note
    """
    def __init__(self, progression, root=None):
      if root is not None:
        self.root = root
        self.prog = [self.root + p for p in progression]
      else:
        self.prog = progression
        self.root = 0

    def __str__(self):
        return "".join([f"{str(i):<4}" for i in self.prog])

    def __getitem__(self, item):
        return self.prog[item]
    
    def __len__(self):
        return len(self.prog)

    def __contains__(self, x):
      if isinstance(x, Note):
        return x.getRootNoteIndex() in self.prog
      elif isinstance(x, NoteSet):
        return sum(1 for i in x.prog if i in self.prog) == len(x.prog)
      else:
        return False

    def getRootNoteIndex(self):
        return self.root

def changeRootNote(noteset, index):
  if index > len(noteset.prog) or index < 0:
    raise Exception("Invalid Index to change root note")
  if index == 0:
    return NoteSet(noteset.prog)

  newProg = noteset.prog[index:] + noteset.prog[:index]
  return NoteSet(newProg)
  
natural_scale   = [0, 2, 4, 5, 7, 9, 11]
# minor_melodic   = [0, 2, 3, 5, 7, 9, 10]
# minor_harmonic  = [0, 2, 3, 5, 7, 8, 11]
# major_harmonic  = [0, 2, 3, 5, 7, 8, 11]

def parseScaleListWH(notesList):
  res = [0]
  for i in notesList:
      halfs = i.count('H')
      fulls = i.count('W')
      res.append(res[-1] + halfs + fulls*2)
  return res

def parseScaleList(notesList, reference):
  if 'W' in notesList[0] or 'H' in notesList[0]:
      return parseScaleListWH(notesList)

  res = []
  for i in notesList:
      i = i.replace(' ','')
      flats = i.count('b')
      sharps = i.count('#')
      num = int(i.replace('b','').replace('#','')) - 1
      res.append(reference[num] - flats + sharps)
  res.sort()
  return res

class Scale:
  def __init__(self, progression, name=None, reference = natural_scale): #reference is major
      if isinstance(progression, list) or isinstance(progression, tuple):
          if isinstance(progression[0], int):
              if all(i in [0,1] for i in progression): #In case its a binary scale
                  assert len(progression) == 12
                  # progression should be something like [x1, x2 .. x12] 
                  # where each xi in {0, 1}
                  self.prog = [index for index, i in enumerate(progression) if i == 1]
              else:
                  self.prog = list(progression)
          elif isinstance(progression[0], str):
              self.prog = parseScaleList(progression, reference)
          else:
              raise Exception(f"Unknown dtype for progression[0]: {type(progression[0])}")
      elif isinstance(progression, str):
          self.prog = parseScaleList(progression.split(','), reference)
      else:
          raise Exception(f"Unknown dtype for progression: {type(progression)}")
      self.name = name
      self.aliases = []

  def addAlias(self, alias):
      self.aliases.append(alias)

  def __str__(self):
      # prog = [f"{i:>3}" for i in self.progression]
      name = self.name or "Unnamed"
      return f"{name:15}: {self.prog}"

  def __getitem__(self, item):
      return self.prog[item]
  
  def __len__(self):
      return len(self.prog)

  def mode(self, num=1, name=None):
      assert num > 0 and num <= len(self.prog)
      num -= 1
      root = self.prog[num]
      
      prog = [i - root for i in self.prog[num:]] \
          + [i - root + 12 for i in self.prog[:num]]
      # print(prog)
      return Scale(prog, name=name)
  
  def distance(self, other):
      assert len(self) == len(other)
      dist = 0
      for i in range(len(self)):
          if self[i] != other[i]:
              dist += 1
      return dist

  def obtainRelativeName(self, other):
      assert len(self) == len(other)
      mods = []
      for i in range(len(self)):
          if self[i] != other[i]:
              dist = self[i] - other[i]
              if dist < 0:
                  mod = 'b' * (-dist)
              # elif dist == 0:
              #     mod = '♮'
              else:
                  mod = '#' * dist
              mods.append(f"{mod}{i+1}")
      return other.name + " " + " ".join(mods)

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