# odex25-Authority
  - created 15-6-2023

## > This is the details of the servers and databases [$${\color{The new domains is not working temporarily}Red}$$]
    - development server    --> auth-dev.exp-sa.com      -OR-  auth-dev.exp-sa.com/web/database/selector
    - preprod server        --> auth-stg.exp-sa.com      -OR-  auth-stg.exp-sa.com/web/database/selector
    - master server         --> auth-sys.exp-sa.com      -OR-  auth-sys.exp-sa.com/web/database/selector
  [$${\color{The domains that is currently working}Red}$$] :
        * development server    --> $${\color{authority-dev.exp-sa.com/web/database/selector}Light \space Green}$$
        * preprod server        --> $${\color{authority.exp-sa.com/web/database/selector}Light \space Green}$$
---
## > Our stated policy for organizing development operations on all projects under development:

- #### Branches and development processes:
  - **Master** branch is ***Not*** used in any of the development or testing processes, and is ***only*** used by the development manager.

  - **Preprod** branch is used as a ***stage*** to prepare the launch on the client server, data transfers to it are done under the following criteria :   
    - **pushing** requests are allowed and done automatically by **GitHub Actions**.
    - ***More Will Be Added Very Soon...***


  - **Test** branch is used for ***all*** development processes under the following criteria : 
    - **pulling** or **merging** requests are ***closed*** by default and require the approval of the Development Manager (Eng.Hassan Salah). [***If it isn't already closed now, it will be very soon***]. 
    - **pushing** requests are allowed and done automatically by **GitHub Actions**.

- ##### We recomend to use "GitHub Issues" to "track ideas, feedback, tasks, or bugs for work on GitHub" related to each repo.
        https://docs.github.com/en/issues/tracking-your-work-with-issues/about-issues   

- ##### We highly recommend reviewing this content to ensure clarity of principle of ***"Virsion Control"*** (Git) : 
      - https://mega.nz/folder/XWBFCRqS#7dd5jqa9-jfqSzocRw7SNw      : Simple and clear explanations
      - https://youtu.be/Q6G-J54vgKc                                : Full and extensive explanation
      - https://www.atlassian.com/git/tutorials/syncing/git-pull    : Git Pull command in details
---
---
##### **ADDONS PATH** :

                /ho

