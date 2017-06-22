#coding: utf-8
from __future__ import print_function

from os import path,makedirs

from .masterblock import MasterBlock

class Saver(MasterBlock):
  """
  Will save the incomming data to a file (default csv)

  Can only take ONE input. If the folders do not exist, they will be created.
  If the file exists, the actual file will be named with a trailing number
  to avoid overriding it.
  Args:
    filename: Path and name of the output file

    delay: (default=5) Delay between each writes (in seconds)

    labels: (default='t(s)') What labels to save
    If labels is a string, all the data will be saved, but with this one
    in first place. If it is a list, only these labels will be saved, in
    that order.
  """
  def __init__(self,filename,delay=5,labels='t(s)'):
    """
    """
    MasterBlock.__init__(self)
    self.delay = delay
    self.filename = filename
    self.labels = labels

  def prepare(self):
    if not path.exists(path.dirname(self.filename)):
      # Create the folder if it does not exist
      makedirs(path.dirname(self.filename))
    if path.exists(self.filename):
      # If the file already exists, append a number to the name
      print("[saver] WARNING!",self.filename,"already exists !")
      name,ext = path.splitext(self.filename)
      i = 1
      while path.exists(name+"_%05d"%i+ext):
        i += 1
      self.filename = name+"_%05d"%i+ext
      print("[saver] Using",self.filename,"instead!")

  def begin(self):
    self.last_save = self.t0
    r = self.inputs[0].recv_delay(self.delay) # To know the actual labels
    if self.labels:
      if not isinstance(self.labels,list):
        if self.labels in r.keys():
          # If one label is specified, place it first and
          # add the others alphabetically
          self.labels = [self.labels]
          for k in r.keys():
            if not k in sorted(self.labels):
              self.labels.append(k)
        else:
          # If not a list but not in labels, forget it and take all the labels
          self.labels = list(sorted(r.keys()))
        # if it is a list, keep it untouched
    else:
      # If we did not give them (False, [] or None):
      self.labels = list(sorted(r.keys()))
    self.write_labels()
    self.save(r)

  def loop(self):
    r = self.inputs[0].recv_delay(self.delay)
    self.save(r)

  def write_labels(self):
    with open(self.filename,'w') as f:
      f.write(", ".join(self.labels)+"\n")

  def save(self,d):
    with open(self.filename,'a') as f:
      for i in range(len(d[self.labels[0]])):
        for j,k in enumerate(self.labels):
          f.write((", " if j else "")+str(d[k][i]))
        f.write("\n")