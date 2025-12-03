---
name: greeting
title: Greeting Prompt
description: Generate a personalized greeting message
arguments:
  - name: user
    description: Name of the user
  - name: project
    description: Project name
    default: MyApp
---

Say: Hello {user}! Welcome to {project}. Hope you enjoy your stay!
