import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

path = 'data/input/word_lists'
words = pd.read_excel(f'{path}/two_syllables_words.xlsx')

letter_count = {}
for col in words.columns:
    col_count = []
    for word in words[col].values:
        col_count.append(len(word))
    letter_count[col] = col_count

df = pd.DataFrame(letter_count)
df_long = pd.melt(df, var_name='category', value_name='count')

fig, ax = plt.subplots(figsize=(4.7, 3))
sns.barplot(data=df, ax=ax, width=0.4, fill=False, color='k', capsize=0.1)
#sns.barplot(data=df_long, x='category', y='count', ax=ax, width=0.4, fill=False, color='k', capsize=0.1)
sns.swarmplot(data=df_long, x='category', y='count', ax=ax, alpha=0.7, color='grey')
sns.despine()
ax.set_title('Letter count per category')
for tick in ax.get_xticklabels():
    tick.set_rotation(30)
    tick.set_fontsize(10)
ax.set_xlabel('')
plt.tight_layout()
fig.savefig(f'{path}/letter_count.png', dpi=300)
plt.show()