"""
example string = 'aabbccdeefghij'

Longest Substring Without Repeating Characters
Problem: Return length of longest substring with all unique chars.
"""

def length_of_longest_substring(s):
    char_set = set()
    left = 0
    max_length = 0

    for right in range(len(s)):
        # if we have duplicates then
        while s[right] in char_set:
            char_set.remove(s[left])
            left += 1
        char_set.add(s[right])
        max_length = max(max_length, right-left+1)

    return max_length

s = 'aabbccdeefghij'
s2 = "abcdefghij"
print(length_of_longest_substring(s2))