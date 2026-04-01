# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

Class 1: Pet: has attributes: owner_ids, pet_id, age, owner, task. Methods: getters that resturn the needs and the time they should be completed
another method that updates whether the task was met or not. 
Class 2: User: has attributes: onwner_id, pet_ids, schedule methods: 1- should return the free times of the user and match that with the pet. 
2- another method that creates a task for the pet based on the needs of the pet and the free time of the user.

Class 3: Task: has a pet_id, owner_id, type, allocated time, completed or not completed. It has method that keeps track of whether that task was fulfilled or not

Class 4: Scheduler: has a method that takes the user and pet info and creates a schedule based on the needs of the pet and the free time of the user.


**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

It added a priority attribut to the tasks to help the scheduling become more efficient. 
---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?
One constraint is the remaining time capacity (the slot capacity). In additon, it encforces no-overlap detection in detect_conflicts method. 
**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?
The scheduler favors a simple greedy approach that schedules tasks in order of priority and earliest free time. This may leave time unusable if a longer task blocks a better combination of shorter tasks.

This is a tradeoff because it may not always produce the optimal schedule, but it is much simpler to implement and understand. 

Given the constraints of the project and the need for explainability, this tradeoff is reasonable for this scenario.
---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
