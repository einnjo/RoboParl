
import sys

class Token( object ):
   def __init__( self ):
      self.kind   = 0     # token kind
      self.pos    = 0     # token position in the source text (starting at 0)
      self.col    = 0     # token column (starting at 0)
      self.line   = 0     # token line (starting at 1)
      self.val    = u''   # token value
      self.next   = None  # AW 2003-03-07 Tokens are kept in linked list


class Position( object ):    # position of source code stretch (e.g. semantic action, resolver expressions)
   def __init__( self, buf, beg, len, col ):
      assert isinstance( buf, Buffer )
      assert isinstance( beg, int )
      assert isinstance( len, int )
      assert isinstance( col, int )

      self.buf = buf
      self.beg = beg   # start relative to the beginning of the file
      self.len = len   # length of stretch
      self.col = col   # column number of start position

   def getSubstring( self ):
      return self.buf.readPosition( self )

class Buffer( object ):
   EOF      = u'\u0100'     # 256

   def __init__( self, s ):
      self.buf    = s
      self.bufLen = len(s)
      self.pos    = 0
      self.lines  = s.splitlines( True )

   def Read( self ):
      if self.pos < self.bufLen:
         result = self.buf[self.pos]
         self.pos += 1
         return result
      else:
         return Buffer.EOF

   def ReadChars( self, numBytes=1 ):
      result = self.buf[ self.pos : self.pos + numBytes ]
      self.pos += numBytes
      return result

   def Peek( self ):
      if self.pos < self.bufLen:
         return self.buf[self.pos]
      else:
         return Scanner.buffer.EOF

   def getString( self, beg, end ):
      s = ''
      oldPos = self.getPos( )
      self.setPos( beg )
      while beg < end:
         s += self.Read( )
         beg += 1
      self.setPos( oldPos )
      return s

   def getPos( self ):
      return self.pos

   def setPos( self, value ):
      if value < 0:
         self.pos = 0
      elif value >= self.bufLen:
         self.pos = self.bufLen
      else:
         self.pos = value

   def readPosition( self, pos ):
      assert isinstance( pos, Position )
      self.setPos( pos.beg )
      return self.ReadChars( pos.len )

   def __iter__( self ):
      return iter(self.lines)

class Scanner(object):
   EOL     = u'\n'
   eofSym  = 0

   charSetSize = 256
   maxT = 71
   noSym = 71
   start = [
     0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
     0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
     0, 12,  3,  0,  0, 18,  0,  0, 19, 20, 16, 14, 23, 15, 24, 17,
     6,  5,  5,  5,  5,  5,  5,  5,  5,  5,  0,  8, 27, 25, 26,  0,
     0,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,
     1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1, 21,  0, 22,  0,  0,
     0,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,
     1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  0,  0,  0,  0,  0,
     0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
     0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
     0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
     0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
     0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
     0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
     0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
     0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
     -1]


   def __init__( self, s ):
      self.buffer = Buffer( unicode(s) ) # the buffer instance

      self.ch        = u'\0'       # current input character
      self.pos       = -1          # column number of current character
      self.line      = 1           # line number of current character
      self.lineStart = 0           # start position of current line
      self.oldEols   = 0           # EOLs that appeared in a comment;
      self.NextCh( )
      self.ignore    = set( )      # set of characters to be ignored by the scanner
      self.ignore.add( ord(' ') )  # blanks are always white space
      self.ignore.add(9) 
      self.ignore.add(10) 
      self.ignore.add(13) 

      # fill token list
      self.tokens = Token( )       # the complete input token stream
      node   = self.tokens

      node.next = self.NextToken( )
      node = node.next
      while node.kind != Scanner.eofSym:
         node.next = self.NextToken( )
         node = node.next

      node.next = node
      node.val  = u'EOF'
      self.t  = self.tokens     # current token
      self.pt = self.tokens     # current peek token

   def NextCh( self ):
      if self.oldEols > 0:
         self.ch = Scanner.EOL
         self.oldEols -= 1
      else:
         self.ch = self.buffer.Read( )
         self.pos += 1
         # replace isolated '\r' by '\n' in order to make
         # eol handling uniform across Windows, Unix and Mac
         if (self.ch == u'\r') and (self.buffer.Peek() != u'\n'):
            self.ch = Scanner.EOL
         if self.ch == Scanner.EOL:
            self.line += 1
            self.lineStart = self.pos + 1
      



   def Comment0( self ):
      level = 1
      line0 = self.line
      lineStart0 = self.lineStart
      self.NextCh()
      while True:
         if ord(self.ch) == 10:
            level -= 1
            if level == 0:
               self.oldEols = self.line - line0
               self.NextCh()
               return True
            self.NextCh()
         elif self.ch == Buffer.EOF:
            return False
         else:
            self.NextCh()

   def Comment1( self ):
      level = 1
      line0 = self.line
      lineStart0 = self.lineStart
      self.NextCh()
      if self.ch == '*':
         self.NextCh()
         while True:
            if self.ch == '*':
               self.NextCh()
               if self.ch == '/':
                  level -= 1
                  if level == 0:
                     self.oldEols = self.line - line0
                     self.NextCh()
                     return True
                  self.NextCh()
            elif self.ch == '/':
               self.NextCh()
               if self.ch == '*':
                  level += 1
                  self.NextCh()
            elif self.ch == Buffer.EOF:
               return False
            else:
               self.NextCh()
      else:
         if self.ch == Scanner.EOL:
            self.line -= 1
            self.lineStart = lineStart0
         self.pos = self.pos - 2
         self.buffer.setPos(self.pos+1)
         self.NextCh()
      return False


   def CheckLiteral( self ):
      lit = self.t.val
      if lit == "Program":
         self.t.kind = 5
      elif lit == "End":
         self.t.kind = 6
      elif lit == "Var":
         self.t.kind = 7
      elif lit == "Robot":
         self.t.kind = 10
      elif lit == "Int":
         self.t.kind = 11
      elif lit == "Double":
         self.t.kind = 12
      elif lit == "Bool":
         self.t.kind = 13
      elif lit == "String":
         self.t.kind = 14
      elif lit == "Void":
         self.t.kind = 15
      elif lit == "List":
         self.t.kind = 16
      elif lit == "True":
         self.t.kind = 30
      elif lit == "False":
         self.t.kind = 31
      elif lit == "Task":
         self.t.kind = 35
      elif lit == "If":
         self.t.kind = 36
      elif lit == "Else":
         self.t.kind = 37
      elif lit == "While":
         self.t.kind = 38
      elif lit == "For":
         self.t.kind = 39
      elif lit == "In":
         self.t.kind = 40
      elif lit == "Print":
         self.t.kind = 41
      elif lit == "Read":
         self.t.kind = 42
      elif lit == "Return":
         self.t.kind = 43
      elif lit == "Break":
         self.t.kind = 44
      elif lit == "lookRight":
         self.t.kind = 46
      elif lit == "lookLeft":
         self.t.kind = 47
      elif lit == "lookBack":
         self.t.kind = 48
      elif lit == "lookNorth":
         self.t.kind = 49
      elif lit == "lookEast":
         self.t.kind = 50
      elif lit == "lookSouth":
         self.t.kind = 51
      elif lit == "lookWest":
         self.t.kind = 52
      elif lit == "look":
         self.t.kind = 53
      elif lit == "paintFront":
         self.t.kind = 54
      elif lit == "paintHere":
         self.t.kind = 55
      elif lit == "paintBack":
         self.t.kind = 56
      elif lit == "paintRight":
         self.t.kind = 57
      elif lit == "paintLeft":
         self.t.kind = 58
      elif lit == "Red":
         self.t.kind = 59
      elif lit == "Green":
         self.t.kind = 60
      elif lit == "Blue":
         self.t.kind = 61
      elif lit == "paint":
         self.t.kind = 62
      elif lit == "wallFront":
         self.t.kind = 63
      elif lit == "wallBack":
         self.t.kind = 64
      elif lit == "wallLeft":
         self.t.kind = 65
      elif lit == "wallRight":
         self.t.kind = 66
      elif lit == "wall":
         self.t.kind = 67
      elif lit == "moveFront":
         self.t.kind = 68
      elif lit == "moveBack":
         self.t.kind = 69
      elif lit == "move":
         self.t.kind = 70


   def NextToken( self ):
      while ord(self.ch) in self.ignore:
         self.NextCh( )
      if (self.ch == '#' and self.Comment0() or self.ch == '/' and self.Comment1()):
         return self.NextToken()

      self.t = Token( )
      self.t.pos = self.pos
      self.t.col = self.pos - self.lineStart + 1
      self.t.line = self.line
      if ord(self.ch) < len(self.start):
         state = self.start[ord(self.ch)]
      else:
         state = 0
      buf = u''
      buf += unicode(self.ch)
      self.NextCh()

      done = False
      while not done:
         if state == -1:
            self.t.kind = Scanner.eofSym     # NextCh already done
            done = True
         elif state == 0:
            self.t.kind = Scanner.noSym      # NextCh already done
            done = True
         elif state == 1:
            if (self.ch >= '0' and self.ch <= '9'
                 or self.ch >= 'A' and self.ch <= 'Z'
                 or self.ch == '_'
                 or self.ch >= 'a' and self.ch <= 'z'):
               buf += unicode(self.ch)
               self.NextCh()
               state = 1
            else:
               self.t.kind = 1
               self.t.val = buf
               self.CheckLiteral()
               return self.t
         elif state == 2:
            if (self.ch >= '1' and self.ch <= '9'):
               buf += unicode(self.ch)
               self.NextCh()
               state = 2
            elif self.ch == '0':
               buf += unicode(self.ch)
               self.NextCh()
               state = 7
            else:
               self.t.kind = 3
               done = True
         elif state == 3:
            if (self.ch >= ' ' and self.ch <= '!'
                 or self.ch >= '#' and self.ch <= '&'
                 or self.ch >= '(' and self.ch <= '>'
                 or self.ch >= '@' and self.ch <= '['
                 or self.ch >= ']' and self.ch <= '_'
                 or self.ch >= 'a' and self.ch <= '{'
                 or self.ch == '}'):
               buf += unicode(self.ch)
               self.NextCh()
               state = 3
            elif self.ch == '"':
               buf += unicode(self.ch)
               self.NextCh()
               state = 4
            else:
               self.t.kind = Scanner.noSym
               done = True
         elif state == 4:
            self.t.kind = 4
            done = True
         elif state == 5:
            if (self.ch >= '0' and self.ch <= '9'):
               buf += unicode(self.ch)
               self.NextCh()
               state = 5
            elif self.ch == '.':
               buf += unicode(self.ch)
               self.NextCh()
               state = 2
            else:
               self.t.kind = 2
               done = True
         elif state == 6:
            if self.ch == '.':
               buf += unicode(self.ch)
               self.NextCh()
               state = 2
            else:
               self.t.kind = 2
               done = True
         elif state == 7:
            if (self.ch >= '1' and self.ch <= '9'):
               buf += unicode(self.ch)
               self.NextCh()
               state = 2
            elif self.ch == '0':
               buf += unicode(self.ch)
               self.NextCh()
               state = 7
            else:
               self.t.kind = 3
               done = True
         elif state == 8:
            self.t.kind = 9
            done = True
         elif state == 9:
            self.t.kind = 19
            done = True
         elif state == 10:
            self.t.kind = 20
            done = True
         elif state == 11:
            self.t.kind = 21
            done = True
         elif state == 12:
            if self.ch == '=':
               buf += unicode(self.ch)
               self.NextCh()
               state = 13
            else:
               self.t.kind = Scanner.noSym
               done = True
         elif state == 13:
            self.t.kind = 22
            done = True
         elif state == 14:
            self.t.kind = 23
            done = True
         elif state == 15:
            self.t.kind = 24
            done = True
         elif state == 16:
            self.t.kind = 25
            done = True
         elif state == 17:
            self.t.kind = 26
            done = True
         elif state == 18:
            self.t.kind = 27
            done = True
         elif state == 19:
            self.t.kind = 28
            done = True
         elif state == 20:
            self.t.kind = 29
            done = True
         elif state == 21:
            self.t.kind = 32
            done = True
         elif state == 22:
            self.t.kind = 33
            done = True
         elif state == 23:
            self.t.kind = 34
            done = True
         elif state == 24:
            self.t.kind = 45
            done = True
         elif state == 25:
            if self.ch == '=':
               buf += unicode(self.ch)
               self.NextCh()
               state = 11
            else:
               self.t.kind = 8
               done = True
         elif state == 26:
            if self.ch == '=':
               buf += unicode(self.ch)
               self.NextCh()
               state = 9
            else:
               self.t.kind = 17
               done = True
         elif state == 27:
            if self.ch == '=':
               buf += unicode(self.ch)
               self.NextCh()
               state = 10
            else:
               self.t.kind = 18
               done = True

      self.t.val = buf
      return self.t

   def Scan( self ):
      self.t = self.t.next
      self.pt = self.t.next
      return self.t

   def Peek( self ):
      self.pt = self.pt.next
      while self.pt.kind > self.maxT:
         self.pt = self.pt.next

      return self.pt

   def ResetPeek( self ):
      self.pt = self.t

