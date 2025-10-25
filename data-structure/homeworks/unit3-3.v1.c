/*
 * @Author: aquamarine5 && aquamarine5_@outlook.com
 * Copyright (c) 2025 by @aquamarine5, RC. All Rights Reversed.
 * lovely lonely, but be a quokka.
 */
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

// 函数声明
void ComputeNext(const char *p, int *next);
char *LongestCommonSubstring(const char *s, const char *t);

/**
 * @brief 计算KMP算法中的next数组（前缀函数）
 *
 * @param p 模式字符串
 * @param next 存储next值的数组
 */
void ComputeNext(const char *p, int *next)
{
    int m = strlen(p);
    int k = 0;
    int q;
    next[0] = 0;
    for (q = 1; q < m; q++)
    {
        while (k > 0 && p[k] != p[q])
        {
            k = next[k - 1];
        }
        if (p[k] == p[q])
        {
            k++;
        }
        next[q] = k;
    }
}
void Getnext(int next[], char t[])
{
    int j = 1, k = 0;
    // j=1,k=0
    next[0] = -1;
    // next[1]=0
    while (j < strlen(t) - 1) // j<t[0]
    {
        // k==0
        if (k == -1 || t[j] == t[k])
        // 等于-1就不继续了，直接k++；  next[j] = k=0了;
        // 不是-1还相同的话就直接k++；注意j先++了，所以是改变的下一个值。
        {
            j++;
            k++;
            next[j] = k;
        }
        else
            k = next[k];
    }
}
/**
 * @brief 使用KMP的next数组思想查找两个字符串s和t的最长公共子串
 *
 * @param s 第一个字符串
 * @param t 第二个字符串
 * @return char* 指向最长公共子串的指针。该内存是动态分配的，使用后需要调用 free() 释放。
 *               如果没有公共子串，则返回一个空字符串。
 */
char *LongestCommonSubstring(const char *s, const char *t)
{
    int len_s = strlen(s);
    int len_t = strlen(t);
    int max_len = 0;
    int start_pos_s = -1;
    char *temp_str;
    int *next;
    int i;

    // 遍历s的每一个后缀
    for (i = 0; i < len_s; i++)
    {
        int suffix_len = len_s - i;
        int temp_len = len_t + 1 + suffix_len;
        int j;

        // 为每个后缀构造临时字符串: t + '#' + s的后缀
        temp_str = (char *)malloc(temp_len + 1);
        next = (int *)malloc(temp_len * sizeof(int));

        strcpy(temp_str, t);
        strcat(temp_str, "#");
        strcat(temp_str, s + i);

        ComputeNext(temp_str, next);

        // 在next数组中查找最大值
        for (j = len_t + 1; j < temp_len; j++)
        {
            if (next[j] > max_len)
            {
                max_len = next[j];
                // 计算最长公共子串在s中的起始位置
                start_pos_s = i + (j - (len_t + 1)) - (max_len - 1);
            }
        }

        free(temp_str);
        free(next);
    }

    // 根据找到的最大长度和起始位置，创建并返回结果字符串
    char *result = (char *)malloc((max_len + 1) * sizeof(char));
    if (max_len > 0)
    {
        strncpy(result, s + start_pos_s, max_len);
        result[max_len] = '\0';
    }
    else
    {
        result[0] = '\0';
    }

    return result;
}

int main()
{
    const char *s = "abacde";
    const char *t = "bacdae";
    char *common_substring;

    printf("字符串s: %s\n", s);
    printf("字符串t: %s\n", t);

    common_substring = LongestCommonSubstring(s, t);

    if (strlen(common_substring) > 0)
    {
        printf("最长公共子串是: %s\n", common_substring);
    }
    else
    {
        printf("没有找到公共子串。\n");
    }

    free(common_substring);

    // 另一个测试用例
    const char *s2 = "testing123";
    const char *t2 = "thisisatest";
    printf("\n字符串s2: %s\n", s2);
    printf("字符串t2: %s\n", t2);
    common_substring = LongestCommonSubstring(s2, t2);
    if (strlen(common_substring) > 0)
    {
        printf("最长公共子串是: %s\n", common_substring);
    }
    else
    {
        printf("没有找到公共子串。\n");
    }
    free(common_substring);

    return 0;
}