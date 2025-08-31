Whenever this rule file is executed, it should look at the last task that was done.
If the task includes code changes, logic implementation, data processing, API development, configuration changes, or any backend/non-visual work, then the output should list things that need to be tested.

The output should always say things like:

"The unit tests need to be run and verified."

"The integration tests need to pass."

"The error handling needs to be checked."

"The edge cases need to be covered."

"The performance impact needs to be measured."

"The code quality and linting need to pass."

"The security implications need to be reviewed."

After listing those, it should always ask for feedback in a clear way, like:

"Give me feedback on the logic and implementation."

"Give me feedback on the performance and efficiency."

"Give me feedback on the error handling and edge cases."

"Give me feedback on the code quality and maintainability."

The output should always follow this structure:

First, list all the things that need to be tested.
Then, list all the things you want feedback on.

If the last task was visual (UI, canvas, layout), then don't output anything.