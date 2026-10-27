| Family | Cases x runs | Before: bare assistant | After: guard layer | Successes per run after |
| --- | --- | --- | --- | --- |
| direct_injection | 60 | 53/60 = 88.3% [77.8%, 94.2%] | 0/60 = 0.0% [0.0%, 6.0%] | 0, 0, 0 |
| indirect_injection | 60 | 10/60 = 16.7% [9.3%, 28.0%] | 0/60 = 0.0% [0.0%, 6.0%] | 0, 0, 0 |
| roleplay | 60 | 38/60 = 63.3% [50.7%, 74.4%] | 0/60 = 0.0% [0.0%, 6.0%] | 0, 0, 0 |
| cross_customer | 60 | 57/60 = 95.0% [86.3%, 98.3%] | 0/60 = 0.0% [0.0%, 6.0%] | 0, 0, 0 |
| prompt_extraction | 60 | 16/60 = 26.7% [17.1%, 39.0%] | 0/60 = 0.0% [0.0%, 6.0%] | 0, 0, 0 |

| Benign suite | Before | After | Limit written in advance | Within the limit |
| --- | --- | --- | --- | --- |
| False blocks, all 100 questions x 3 runs | 0/300 = 0.0% | 7/300 = 2.3% [1.1%, 4.7%] | 3.0% | yes |
| False blocks, the 20 risky-looking questions | 0/60 = 0.0% | 7/60 = 11.7% [5.8%, 22.2%] | | |
