import pandas as pd
import filereader
# This file will contain functions and routines to gather subsets of the data
# that can be used in statistical analysis to answer certain
# specific questions, such as "does it matter if you use a rare or a common?"

def look_for_outcome(df: pd.DataFrame, monster: str) -> pd.DataFrame:
    """
    Look for all breeding attempts that result in a single, specific monster.
    """
    mask = []
    for _, row in df.iterrows():
        mask.append(monster in row["Possible results"])
    return df[mask]

def get_n_elements(full_monster_set: list, amount: int) -> list:
    new_list = []
    for monster in full_monster_set:
        if monster in filereader.elements:
            if len(filereader.elements[monster]) == amount:
                new_list.append(monster)
    return new_list

def alias_parser(alias: str) -> list:
    """
    Return the group of monsters associated with an alias.
    Aliases can be used for some groups of monsters.
    
    Example aliases:
    Common Ethereals
    Epic Fire triples
    Rare Magical
    
    Available aliases:
    Paironormals
    Shugafam
    (Common/Rare/Epic) Ethereals (singles/doubles)
    (Common/Rare/Epic) (Dream)Mythicals
    (Common/Rare/Epic) Seasonals
    (Common/Rare/Epic) (Natural/Fire/Magical) (singles/doubles/triples/quads)
    Epic Fire Expansion

    Note: Fire Expansion Monsters are (currently) not categorized as Fire monsters.
    """
    rarity_indicators = ["Common", "Rare", "Epic"]
    count_indicators = {"singles":1, "doubles":2, "triples":3, "quads":4, "quints":5}
    group_indicators = list(filereader.groups["group name"])
    full_monster_set = set()
    for group in group_indicators:
        full_monster_set = set.union(full_monster_set, set(*filereader.get_group(group)))
    # Do aliases
    selected_monsters = full_monster_set.copy()
    # Groups: have a groups file
    
    alias_parts = alias.split(" ")
    # Get group indicator
    if "Expansion" in alias_parts:
        selected_monsters.intersection_update(filereader.get_group("Fire Expansion"))
    else:
        for group in group_indicators:
            if group in alias_parts:
                selected_monsters.intersection_update(set(*filereader.get_group(group)))
    # Do element counts
    for count, amount in count_indicators.items():
        if count in alias_parts:
            n_elementals = get_n_elements(full_monster_set, amount)
            selected_monsters.intersection_update(n_elementals)
    # Do rarity
    rarity_added = False
    for rarity in rarity_indicators:
        if rarity in alias_parts:
            if rarity != "Common":
                selected_monsters = {rarity + " " + monster for monster in selected_monsters}
            rarity_added = True
    if not rarity_added:
        selected_monsters = selected_monsters.union({"Rare "+monster for monster in selected_monsters}.union({"Epic "+monster for monster in selected_monsters}))
    monsters = list(selected_monsters)
    return monsters

def look_for_outcome_group(df: pd.DataFrame, monsters: list | str) -> pd.DataFrame:
    """
    Look for a group of monsters in the possible breeding results.
    Aliases can be used for some groups.
    
    Example aliases:
    Common Ethereals
    Epic Fire triples
    Rare Magical
    
    Available aliases:
    Paironormals
    Shugafam
    (Common/Rare/Epic) Ethereals (singles/doubles)
    (Common/Rare/Epic) (Dream)Mythicals
    (Common/Rare/Epic) Seasonals
    (Common/Rare/Epic) (Natural/Fire/Magical) (singles/doubles/triples/quads)
    Epic Fire Expansion

    Note: Fire Expansion Monsters are (currently) not categorized as Fire monsters.
    """
    
    if type(monsters) is str:
        monsters = alias_parser(monsters)

    result_dfs = []
    for monster in monsters:
        result_dfs.append(look_for_outcome(df, monster))
    return pd.concat(result_dfs)

def constant_torches(df: pd.DataFrame, torch_amount: int | None = None) -> pd.DataFrame:
    """
    Look for all breeding attempts that have a certain amount of torches.
    Titan skins are a thing though and I haven't decided on how to treat them yet.

    Parameters
    ----------
    df: pd.DataFrame
        Dataframe to look into. Should have a column "Torches".
    
    torch_amount: int | None, default None
        The amount of torches to look for. If None, finds the amount of torches with
        the largest amount of datapoints.
    """
    if type(torch_amount) is int:
        return df[df["Torches Lit"] == torch_amount]
    else:
        counts = df["Torches Lit"].value_counts()
        largest_amount = counts.index[0]
        print("Most data found with {} torches: there's {} observations".format(largest_amount, counts.iloc[0]))
        return df[df["Torches Lit"] == largest_amount]

def constant_levels(df: pd.DataFrame, level1: int | None = None, level2: int | None = None) -> pd.DataFrame:
    """
    Look for all breeding attempts that have parents of a certain level.

    Parameters
    ----------
    df: pd.DataFrame
        Dataframe to look into. Should have columns "Parent 1 Level" and "Parent 2 Level"

    level1, level2: int | None, default None
        The parent levels to look for. If None, finds the combination with the
        highest amount of datapoints. Currently does not look for combinations
        where parent 1 is of level level2 and parent 2 is of level level1,
        but this might change in the future.
    """