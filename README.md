# Simplified Lexurgy

## Overview
*Simplified Lexurgy* is a simplified version of the utility [Lexurgy](https://www.lexurgy.com) which allows users to simulate the effects of sound changes on a set of words. This is a truncated version of that tool, possessing far fewer features.

## Introduction
This document works as a reference manual for Simplified Lexurgy. The grammar is extremely easy to parse. A few examples can be seen below:

```
Feature type(cons, vowel)
Symbol x [cons]
Symbol y [vowel]

label1:
    [cons] [vowel] [cons] [vowel] => [cons] [cons] [vowel] [vowel] / _ $ // $ _
```

The above grammar takes any substring `xyxy` at the end of a word and transforms it into `xxyy`, unless said substring is also at the beginning of the word. More specifically, it loops through the entire word, looking for instances of `xyxy` and transforming them into `xxyy`.