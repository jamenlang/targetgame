#!/usr/bin/python
import RPi.GPIO as GPIO
import os
import time
import random
import pygame

os.chdir("/home/pi/targetgame")
GPIO.setmode(GPIO.BCM)
pygame.mixer.init()

#gpio pin the target switch is on
target = 18
#gpio pin the LED will be on
led = 24
#set hitpoints for target
hp = 30

GPIO.setup(led, GPIO.OUT)
GPIO.setup(target, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

prev_input = 0
absorb = False

#game is starting. play some awesome music.

pygame.mixer.music.load('loop.wav')
pygame.mixer.music.play(-1)


def damagemode( hp , prev_input , iterations):
 print("Damage mode is ON")
 print("Iterations %d") % iterations
 while (iterations != 0):
  input = GPIO.input(target)
  #print input
  if ((not prev_input) and input):
   print "Input: %d" % input
   print("Target Damaged!")
   hp = hp - 1
   print "HP Down to %d" % hp
   soundObj = pygame.mixer.Sound("hit.wav")
   soundObj.play()

   prev_input = input
   return ( hp, prev_input )

   #slight pause to debounce
   time.sleep(0.05)
  iterations = iterations - 1
  #print iterations
 return ( hp, prev_input )

def absorbmode( hp, prev_input, iterations ):
 print("Absorb mode is ON")
 print("Iterations %d") % iterations
 GPIO.output(led, 1)
 while (iterations != 0):
  input = GPIO.input(target)
  #print input
  if ((not prev_input) and input):
   print("Target absorbed damage!")
   soundObj = pygame.mixer.Sound("absorb.wav")
   soundObj.play()

   hp = hp + 1
   print "HP increased to %d" % hp
   prev_input = input
   GPIO.output(led, 0)
   return ( hp, prev_input )

   #slight pause to debounce
   time.sleep(0.05)
  iterations = iterations - 1
  #print iterations

 GPIO.output(led, 0)
 return ( hp, prev_input )

while True:
 prev_input = 0
 input = GPIO.input(target)
 if ((not prev_input) and input):
  print "input %s, previously %s" % (input, prev_input)
  print "HP: %d" % hp
 iterations = random.randrange(100000, 1000000)
 #print "Iterations: %s" % iterations
 if (bool(random.getrandbits(1)) and absorb != False):
  hp, prev_input = absorbmode( hp, prev_input, iterations )
  absorb = False
 else:
  absorb = bool(random.getrandbits(1))
 hp, prev_input = damagemode( hp, prev_input, iterations )
 print "HP: %d" % hp
 
 if (hp <= 0):
  print("Target Destroyed!")
  #target is dead, stop playing music.
  pygame.mixer.music.load("dead.wav")
  pygame.mixer.music.play()
  while pygame.mixer.music.get_busy() == True:
   continue
  break
 time.sleep(1)

GPIO.cleanup()
