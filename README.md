% DV2(1) DéjàVu-DéjàVu Chatbot/Scriptbot | Version 0.4.20
% Gary Dean
% Oct 2023

# NAME
**DéjàVu-DéjàVu Chatbot/Scriptbot Terminal**

# SYNOPSIS
**`dv2 [agent] [-options] [<script_file]`**

  `agent`

    Agent file (with '.dv2.agent' filename extension).
    Optional, Positional; must be first argument,
    before any other options.

  `script_file`

    script.dv2 file, via stdin. --

| hdr1 | hdr2 | hdr3 |
| AA | BBB | CCCC |
| aaaa | bbb | cc |
| 1 | 2 | 3 |


# OPTIONS
-v, **--verbose**
: Verbose on (default)

-m, **--model** "model"
: openai [model=gpt-3.5-turbo-16k-0613]

-t, **--temperature** N.N
: [temperature=0.0072973525693]

-g, **--message** system|user|assistant "content..."
: eg, -g user "How did I get here?"

-k, **--token_limit** N
: context window [token limit=16000]\n. Usually calculated automatically (see --auto-max-tokens).

-M, **--max_tokens** N
: response tokens [max_tokens=4000] Usually calculated automatically (see --auto-max-tokens).

-c, **--command**, *--cmd* { "/cmd" | "gpt_instruction" }
: Add dv2 /slash command _or_ gpt user prompt to command stack (Cmd_Cache[]). Can be used multiple times.

-L, **--languages** "lang1,lang2,..."
: [languages='English Indonesian']

-x, **--exit_on_completion**, --exit
: [exit_on_completion='0'] Exit upon completion of commands/script.

-v, **--verbose**
: verbose=1 [verbose=1]

-q, **--quiet**
: verbose=0

-N, **--no-statusline**
: statusline=0 [statusline=1]

-i, **--interactive**
: interactive=1 [interactive=1] yes-no prompts are enabled.

-y, **--not-interactive**
: interactive=0 yes-no prompts are disabled; default y.

-a, **--auto-max-tokens**
: auto_max_tokens=1 [auto_max_tokens=1] Enable dynamic calculation of max_tokens to maximum available.
-A, **--no-auto-max-tokens**
: auto_max_tokens=0 Disable dynamic calculation of max_tokens.

-a, **--autosave** on|off
: If on, upon exit, append current messages to current dv script. Default is off.

-u, **--upgrade**
: Upgrade DV2 from git repository. Git repository is set to: https://github.com/Open-Technology-Foundation/dejavu2

-V, **--version**
: [version="dv2 0.4.20"], exit

-h, **--help**
: This help, exit

# DESCRIPTION

    _/////    _//         _//
    _//   _//  _//       _//   _///_/
    _//    _//  _//     _//   _/    _//
    _//    _//   _//   _//         _//
    _//    _//    _// _//        _//
    _//   _//      _////       _//
    _/////          _//       _////////

    D  E  J  A  V  U - D  E  J  A  V  U

DéjàVu-DéjàVu (`DV2`) is an AI Agent-creation and scripting program for the Bash terminal, using openAI GPT models.

DV2 has powerful scripting capabilities.  It brings the power of OpenAi's GPT models directly to your terminal command-line.

    __"it's dejavu all over again."__ - Y. Berra

Remembers context and history.  You and your AI can have multiple 'personalities', 'experts', tasks, etc.

# Requirements
For the moment, DV2 has only been tested on Ubuntu Linux 22.04.

Other requirements are:
  - Python 3.10+
  - Bash 5+
  - git
  - pandoc
  - openai

Before starting, you will need ensure you have an API key from [openAI](https://openai.com/api/) in order to run this program.  See also ENVIRONMENT.

# Installation
Installation One-Liner, if you're in a hurry:

```bash
git clone https://github.com/Open-Technology-Foundation/dejavu2 /tmp/dejavu2 && /tmp/dejavu2/dv2.install
```

`dv2.install` will detect these variables during installation.  If it doesn't, check your environment.

Once that's done, you're ready to install.  `dv2.install` will:

 - Execute `apt update` and `apt upgrade` (disable with --no-apt)
 - Install python 3, pip and git packages (disabled with --no-apt)
 - Modify `~/.bashrc` and `/etc/bash.bashrc` to include openai environment variables.
 - Store program files in `/usr/share/dejavu2`
 - Create symlink `dv2` in `/usr/local/bin`.

# ENVIRONMENT
Before running, make sure you have set up your openAI API key in your system's environment.  If you set up your openAI account as an organization, you will also need to set your organization ID.  Update your environment variables as follows:

```bash
export OPENAI_API_KEY='sk-_your_key_'
export OPENAI_ORGANIZATION_ID='org-_your_org_id_'
```

You may wish to place these declarations into your `.bash.rc` and/or `/etc/bash.bashrc` files.

# EXAMPLES

```bash
# Run interactively with default config Agents
dv2

# Add agent 'mydharma', interactive
dv2 mydharma

# Add agent 'techlead', ask question, and exit.
dv2 techlead -xc 'in python, display syntax, options, usage and examples for .replace()'
```

# OPERATION

## Invocation
  1. Config: Default configuration settings for DV2 are loaded serially from Agent file/s.

  2. Script: If there is input from stdin from a \*.DV2 script file, this is pre-loaded into the DV2 command stack.

  3. Command-line: parameters are processed.

  4. DV2 Stack Execution: If the DV2 command stack is not empty, execution of command stack commences.

  5. DV2 Command Prompt: Manually enter /cmds or instructions to GPT.

### Config
Upon execution, DV2 attempts to load DV2.conf files from the following locations, in this order:

    - ${script_dir}/DV2.conf
    -   /etc/default/DV2.conf
    -     $HOME/.DV2.conf
    -       ./.DV2.conf

If an Agent file has been specified on the command line this is loaded last.

DV2.conf files found on this execution are:

    ${CONF_FILES[*]}

Each Agent inherits all the setting from the previous Agent, thus each subsequent Agent has the ability to set some or all of the available parameters.

### Script
DV2 script files have the extension .DV2, and comprises /commands and gpt queries.

### Command Line

### DV2 Script Execution

### DV2 Command Prompt

# DV2 Script Commands
DV2 script commands are differentiated from GPT instructions by starting with a '/' character (or alternatively, a '!' character).

For instance, `/status` will display all current DV2 settings.

*range* can be in the forms "1,2,3", "4-6", "7-", "-8", "all" and can be combined in any order.

### Help and Status
    /                Short command help.
    /help            Open DV2 help file. Can also use "//"
    /exit            Exit DV2.  Pressing ^C will also exit.
    /status          Show status of current environment.
    /vars            Show current variables.

### Conversations/Messages
    /list [long|short] [range]
                     List current messages.
                     "short" for condenced list, "long" for full list.
                     Default is "long".
                     If "range" omitted, lists entire messages.
    /delete range    Delete message items in "range".
    /clear           Clear all messages.  Same as /delete 1-
    /tldr [range]    Summarize all messages responses in "range".
                     Default is the previous response.
    /summarize [messages|prompt|all]
                     Summarise every message or prompt items.
                     Default is "messages".
    /autosave [on|off]
                     Save all message to current dv Script on exit.
                     Default is Off.
    /save [file]     Save current message.
    /import [file]   Import "file" into the input prompt.
                     If "file" is not specified, opens EDITOR to enable
                     multi-line commands.

### GPT Settings
    /user_name [name] Set/Display user name.
    /ai_name [name]   Set/Display AI name.
    /engine [list|engine|update]
                      Set/Display GPT engine.
    /temperature [f]  Set/Display temperature (0.0-1.0).
    /top_p [f]        Set/Display top_p (0.0-1.0).
    /tokens [n]       Set/Display tokens to use.
    /prompt [prompt]  Display current messages set-up information.
                      If "prompt" is specified, set the new conversion prompt.

### Scripts
    /files           Display messages scripts in current and user home
                     directories, with option to edit.
    /edit [file]     Edit "file". If "file" not specified, edit the current
                     script file.
    /run [file]      Run the "file" script. If not specified, display a list
                     of available scripts.
    /instruction string
                     Insert an instruction. Usually only used in scripts.
    /messages string
                     Add to messages array. Usually only used in scripts.
    /echo [on|off]   Turn command echo on|off. Usually only used in scripts.
    /exec [cmd...]   Execute a shell command.

# Prompt Engineering
Prompt Engineering is a critial part of getting the most out of DV2 and GPT models.  Here are some guidelines:

## 1: Understand the importance of “context”
The most important factor to consider when designing a prompt is context.  Making sure the context is relevant is crucial for getting coherent and accurate responses from GPT.

Without sufficient context, GPT may generate responses that are off-topic, irrelevant, or inconsistent with the goal of the prompt.  To ensure the prompt has an adequate amount of context, include all relevant background information.

## 2: Define a clear task
After providing context, the next step to designing an effective prompt is to define a clear instruction for GPT.

This requires that you have a clear understanding of the task to be completed, and the task definition should be specific, concise, and avoid ambiguity or vagueness.

## 3: Be specific
When designing a prompt make sure the prompt is specific.  The more details and precision included in the prompt, the more likely it is that the GPT will generate a targeted and accurate response.

This includes important details such as what the goal is, the starting and ending points, characters involved, or any relevant background information.  If the prompt is too vague, it will result in off-topic, irrelevant, or inconsistent responses.

## 4: Iterate
Iteration is an effective way of designing an effective prompt.  Prompt design is often an iterative process that involves multiple attempts and cycles of design, testing, and evaluation.

Each iteration offers an opportunity to refine or improve the prompt.  For example, if GPT generates an off-topic response, you could add more specific instructions or additional context to the prompt.

The iterative approach it allows for continuous improvement and optimization of the generated content.

# REQUIRES
Python 3, pip, git, openai API key/s, apt install access

# REPORTING BUGS
Report bugs and deficiencies on the [DV2 github page](https://github.com/Open-Technology-Foundation/dejavu2)

# COPYRIGHT
Copyright © 2022-2023 [Indonesian Open Technology Foundation](https://yatti.id).  License GPLv3+: GNU GPL version 3 or later [GNU Licences](https://gnu.org/licenses/gpl.html).  This is free software: you are free to change and redistribute it.  There is NO WARRANTY, to the extent permitted by law.

# SEE ALSO
  [DV2 github](https://github.com/Open-Technology-Foundation/dejavu2.git)

  [DV2 Webscrape github](https://github.com/Open-Technology-Foundation/dejavu.ai/tree/master/webscrape)

  [YaTTI github](https://github.com/Open-Technology-Foundation/)

  [openAI API](https://openai.com/api/)

