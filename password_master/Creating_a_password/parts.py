#THAT IS NOT THE MAIN FILE 
#DONT RUN THAT!!!
if __name__ == "__main__" :
  print("THAT IS NOT THE MAIN FILE\nDONT RUN THAT!!!")
  exit()
import string
parts = []
symbols = "!@#$%^&*()-_+="
def Uchoice() :
  global parts
  parts = []
  while True :#*for digites choice
    print("Do you want digit in password ? [Y/N] :")
    Dchoice = input("==> :")
    Dchoice = str(Dchoice)
    if Dchoice not in ("Y" , "y" , "N" , "n") :
       print("Wrong answer !")
       print("Just entre [Y OR N]")
       continue
    else :
       break
  while True :#*for upper letters choice
    print("Do you want upper letters in password ? [Y/N] :")
    UPchoice = input("==> :")
    UPchoice = str(UPchoice)
    if UPchoice not in ("Y" , "y" , "N" , "n") :
      print("Wrong answer !")
      print("Just entre [Y OR N]")
      continue
    else :
      break
  while True :#*for lower letters choice
      print("Do you want lower letters in password ? [Y/N] :")
      Lchoice = input("==> :")
      Lchoice = str(Lchoice)
      if Lchoice not in ("Y" , "y" , "N" , "n") :
        print("Wrong answer !")
        print("Just entre [Y OR N]")
        continue
      else :
        break
  while True :#*for symboles choice
      print("Do you want symbole in password ? like(@ , # ...)")
      Schoice = input("==> :")
      Schoice = str(Schoice)
      if Schoice not in ("Y" , "y" , "N" , "n") :
        print("Wrong answer !")
        print("Just entre [Y OR N]")
        continue
      else :
        break
  allchoice = list(Dchoice + UPchoice + Lchoice + Schoice)
  if allchoice[0].lower() == "y":
    parts += string.digits
  if allchoice[1].lower() == "y":
    parts += string.ascii_uppercase
  if allchoice[2].lower() == "y":
    parts += string.ascii_lowercase
  if allchoice[3].lower() == "y":
    parts += symbols



