import filereader

elements = filereader.elements
reverse_elements = filereader.reverse_elements
specials = filereader.specials
always_available = filereader.always_available
special_availabilities = filereader.special_availabilities
existing_rares = filereader.existing_rares

ethereal_pairo={
    "Plant":"Ghazt",
    "Cold":"Grumpyre",
    "Air":"Reebro",
    "Water":"Jeeode",
    "Earth":"Humbug",
    # "Light":"How's the future?",
    "Psychic":"Hairionette",
    "Faerie":"Owlesque",
    "Bone":"Arcorina"
}

natural_singles = ["Noggin", "Toe Jammer", "Mammott", "Potbelly", "Tweedle"]
pairos = ["Hairionette", "Owlesque", "Arcorina"]
ethereal_elements = ["Pl", "Sh", "Me", "Cr", "Po"]

def possible_results(datapoint): 
    parent1 = derare(datapoint["Parent 1 Species"])
    parent2 = derare(datapoint["Parent 2 Species"])
    island = datapoint["Island"]
    demirrored = demirror(island)
    date = datapoint["Date (MSM time) (MM/DD/YYYY)"].date()
    day = datapoint["Day? (Local, 6am-8pm)"]
    night = datapoint["Night? (Local, 6am-8pm)"]

    basic_results = basic_breeding(parent1, parent2)
    special_results = special_breeding(parent1, parent2, demirrored)
    total_results = basic_results + special_results
    rareified_results = rareify(total_results, island == "Shugabush")
    # Apply availability filter
    available_results = []
    for result in rareified_results:
        if result in always_available[demirrored]: # Always available monsters
            available_results.append(result)
        elif result in pairos:
            if island [0:2] == "M " and night is True: # Minor form
                available_results.append(result)
            elif island[0:2] != "M " and day is True: # Major form
                available_results.append(result)
        elif date in special_availabilities: # Event availabilities
            if result in special_availabilities[date]:
                available_results.append(result)
    return available_results

def get_available(date):
    pass

def derare(monster):
    """
    Make a monster the common version.
    """
    if monster[:5] == "Rare ":
        return monster[5:]
    else:
        return monster

def demirror(island):
    if island[:2] == "M ":
        return island[2:]
    else:
        return island

def rareify(monsters, shugabush = False):
    """
    Add the rare version to a list of one or more monsters, if it exists.
    Won't add the common version if a rare is supplied.
    Usually doesn't add the rare version of natural, fire or magical singles,
    except for when input parameter shugabush is set to True.
    """
    extended_rares = existing_rares.copy()
    if shugabush: # Only on Shugabush Island can getting a Mammott or Potbelly result in its rare form
        extended_rares = extended_rares + natural_singles
    new_monsters = []
    if type(monsters) is str: # If just one monster
        if monsters in extended_rares:
            new_monsters = [monsters, "Rare "+monsters]
        else:
            new_monsters = [monsters]
    else: # If a list of monsters
        for monster in monsters:
            new_monsters.append(monster)
            if monster in extended_rares:
                new_monsters.append("Rare "+monster)

    return new_monsters

def basic_breeding(parent1, parent2):
    """
    'Regular' breeding mechanics involving elements.
    Uses the elements of the incoming monsters to determine the outcome.
    """
    # See if both parents have registered elements
    if parent1 in elements and parent2 in elements:
        els1 = elements[parent1]
        els2 = elements[parent2]
        # Rare singles
        if len(els1) == 3 and len(els2) == 3:
            shared_elements = []
            for element in els1:
                if element in els2:
                    shared_elements.append(element)
            rare_singles = ["Rare "+reverse_elements[(element, )] for element in shared_elements]
            return [parent1, parent2] + rare_singles
        else:
            # Check if no shared elements
            for element in els1:
                if element in els2:
                    return [parent1, parent2]
            for element in els2:
                if element in els1:
                    return [parent1, parent2]
            
            # Produce new results
            if els1[0] in ethereal_elements: # Ethereal Island also doesn't breed anything over 2 elements
                if len(els1 + els2) >= 3:
                    return [parent1, parent2]
            new_monster = reverse_elements[tuple(sorted(els1+els2))]
            if parent1 in natural_singles and parent2 in natural_singles:
                return [new_monster] # If parents are two natural singles: only return double
            else:
                return [parent1, parent2, new_monster]
    return [parent1, parent2] # Fallback if parents don't have registered elements

def special_breeding(parent1, parent2, island):
    """
    'Special' breeding mechanics that don't involve elements.
    This includes epics, but also things like shugabush and ethereals.
    Full list:
    Seasonals (respective islands and Seasonal Shanty)
    Mythicals (respective islands and Mythical Island)
    Shugabush (Plant Island and Shugabush Island)
    Ethereals (Only natural islands, Ethereal Island is element-based)
    Paironormals (respective islands)
    Epics

    Parameters
    ----------
    parent1, parent2: str
    Parent names. Should be de-rare-ified.

    island: str
    Island name. Currently only used to determine if it's not Sanctum.

    Returns
    -------
    special_result: list
    List of probably but not certainly length 1 containing all special breeding results.
    Paironormals will not have a form assigned.
    """
    # Just get most of them out of the dict
    special_result = []
    if (parent1, parent2) in specials:
        special_result = specials[(parent1, parent2)]
        # if type(special_result) is not list:
        #     special_result = [special_result]
    # Ethereals + Paironormals get special treatment
    if parent1 in elements and parent2 in elements:
        if (len(elements[parent1]) == 3 and len(elements[parent2]) == 4) or (len(elements[parent1]) == 4 and len(elements[parent2]) == 3):
            if island in ethereal_pairo:
                eth = ethereal_pairo[island]
                special_result = special_result + [eth]
    return special_result

def add_possible_results_to_df(df):
    results_list = []
    for _, row in df.iterrows():
        results = possible_results(row)
        results_list.append(results)
    df['Possible results'] = results_list
    return df

if __name__ == "__main__":
    df = filereader.read_data()
    add_possible_results_to_df(df)
    # print(df[['Parent 1 Species', 'Parent 2 Species', 'Possible results']])
    for _, row in df.iterrows():
        if row["Result Monster"] not in row["Possible results"]:
            print(row[["Parent 1 Species", "Parent 2 Species", "Result Monster"]])