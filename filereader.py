import pandas as pd
import numpy as np


def remove_comments(input_text):
    """
    Remove any comments at the start of a read file.
    Comments at the start of a file are indicated by a % at the start and end.
    
    Parameters
    ----------
    input_text: str or list
        A string or list (the outputs from read and readlines) containing
        the text of the file.
    
    Returns
    -------
    output_text: str
        The same string or list with the comments removed.
    """
    if type(input_text) == str: # If read is used
        start_comment = input_text.find('%')
        if start_comment != -1:
            end_comment = input_text.find('%',start_comment)
            output_text = input_text[end_comment+1:]
        else: # If there are no comments to be removed
            output_text = input_text
    elif type(input_text) == list: # If readlines is used
        i=1
        check = False
        while i<len(input_text) and check == False:
            if input_text[i] == '%\n': # Because of this: only works if end of comment is on a separate line
                check = True
                output_text = input_text[i+1:]
            i+=1
    return output_text


# Import special breeding combinations
def read_specials(include_reverse = False):
    """
    Read the file containing all special breeding combinations.

    Parameters
    ----------
    include_reverse: bool, default False
    Whether or not to return the reverse breeding combination.

    Returns
    -------
    breeding_dict
    Keys are a tuple of monster names, values are monster names.
    Entries are present for (parent1, parent2) and (parent2, parent1).

    reverse_breeding_dict
    Keys are monster names, values are a tuple of monster names.
    """
    with open("specials.txt") as f:
        commented_lines = f.readlines()
    lines = remove_comments(commented_lines)
    breeding_dict = {}
    reverse_breeding_dict = {}
    for line in lines:
        line = line.rstrip('\n')
        parent1, parent2, result = line.split('~')
        breeding_dict.setdefault((parent1, parent2), []).append(result)
        breeding_dict.setdefault((parent2, parent1), []).append(result)
        # # All this is just to deal with combo's that can have multiple special results (looking at you, mythical island)
        # if (parent1, parent2) in breeding_dict:
            
        #     if type(breeding_dict[(parent1, parent2)]) is not list: # If it's a single entry so far
        #         breeding_dict[(parent1, parent2)] = [breeding_dict[(parent1, parent2)], result]
        #         breeding_dict[(parent2, parent1)] = [breeding_dict[(parent2, parent1)], result]
        #     else: # If the current entry already has two or more elements
        #         breeding_dict[(parent1, parent2)] = breeding_dict[(parent1, parent2)] + [result]
        #         breeding_dict[(parent2, parent1)] = breeding_dict[(parent2, parent1)] + [result]
        # else:
        #     breeding_dict[(parent1, parent2)] = result
        #     breeding_dict[(parent2, parent1)] = result
        reverse_breeding_dict[result] = (parent1, parent2)
    if include_reverse:
        return breeding_dict, reverse_breeding_dict
    else:
        return breeding_dict

# Import elements of the guys
def read_elements():
    """
    Read the file containing the elements of all monsters where the elements are
    relevant for breeding.

    Returns
    -------
    monster_dict
    Keys are monster names, values are a tuple of elements

    elements_dict
    Keys are a sorted tuple of elements, values are monster names
    """
    # Warning: Deja-Jin and T-Rox have a dash in their names
    with open("elements.txt") as f:
        commented_lines = f.readlines()
    lines = remove_comments(commented_lines)
    monster_dict = {}
    elements_dict = {}
    for line in lines:
        line = line.rstrip('\n')
        monster, elements = line.split('~')
        element_tuple = tuple(sorted(elements.split(',')))
        monster_dict[monster] = element_tuple
        elements_dict[element_tuple] = monster
    return monster_dict, elements_dict

def read_existing_rares():
    with open("existing_rares.txt") as f:
        commented = f.readlines()
    lines = remove_comments(commented)
    return [line.rstrip("\n") for line in lines]

def read_groups():
    df = pd.read_csv("groups.csv")
    listed = []
    for _, row in df.iterrows():
        listed.append(row["monsters"].split(','))
    df["monsters"] = listed
    return df

elements, reverse_elements = read_elements()
specials = read_specials()
existing_rares = read_existing_rares()
groups = read_groups()

def get_group(groupname: str) -> list:
    return list(groups[groups["group name"] == groupname]["monsters"])[0]

def build_monster_list(remaining_elements):
    if len(remaining_elements) == 1:
        return [remaining_elements, []]
    else:
        all_combinations = []
        current_element = remaining_elements[0]
        further_combinations = build_monster_list(remaining_elements[1:])
        for combination in further_combinations:
            all_combinations.append(combination)
            all_combinations.append([current_element] + combination)
        return all_combinations



# Import availability data
def read_availability():
    always_available = {}
    with open("always_available.txt") as f:
        commented_lines = f.readlines()
    lines = remove_comments(commented_lines)
    for line in lines:
        line = line.rstrip('\n')
        island, monsters = line.split('~')
        monster_list = monsters.split(',')
        # Some monsters are defined as elements
        elements = []
        for monster in monster_list:
            if len(monster) == 1 or len(monster) == 2:
                elements.append(monster)
        for element in elements:
            monster_list.remove(element)
        # Get the monsters from the elements
        if len(elements) >= 1:
            element_combinations = build_monster_list(elements)
            element_combinations.remove([])
            if island == "Ethereal":
                new_element_combinations = []
                for combination in element_combinations:
                    if len(combination) <= 2:
                        new_element_combinations.append(combination)
                element_combinations = new_element_combinations
            element_monsters = [reverse_elements[tuple(sorted(comb))] for comb in element_combinations]
            always_available[island] = monster_list + element_monsters
        else:
            always_available[island] = monster_list
        
    special_availabilities = {}
    df = pd.read_csv("availabilities.csv")
    # Get from file: start date, stop date, list of monsters
    df["startdate"] = pd.to_datetime(df["startdate"])
    df["stopdate"] = pd.to_datetime(df["stopdate"])
    monster_lists = []
    for row in df['monsters']:
        monster_lists.append(row.split(","))
    df["monsters"] = monster_lists
    # Get in dict: day, all available monsters
    records = []
    for _, row in df.iterrows():
        days = pd.date_range(row["startdate"], row["stopdate"], freq='D', inclusive='left')
        for day in days:
            records.append((day.date(), row["monsters"]))
    
    for day, monsters in records:
        special_availabilities[day] = special_availabilities.setdefault(day, []) + monsters
    return always_available, special_availabilities


always_available, special_availabilities = read_availability()

def read_data(
            VALIDATE_MSM_DATE = True,
            REMOVE_TIME_SINCE_RESET = True,
            ASSUME_ZERO_TORCHES = True, 
            VALIDATE_PARENTS_EXIST = True,
            VALIDATE_RESULTS_EXIST = True,
            CHECK_M_AIR = True,
            verbose = False,
            ) -> pd.DataFrame:
    

    # stops pandas skipping columns when printing (for checking the dataframe flattening works)
    pd.set_option('display.max_columns', None)

    # sanitization options
    # VALIDATE_MSM_DATE = True  # make sure the provided date exists and is valid
    # REMOVE_TIME_SINCE_RESET = True  # only required for analysing stuff that resets independently of the date - drops column if not required
    # ASSUME_ZERO_TORCHES = True  # assume 0 torches if not provided, removes rows with no torch values if False
    # VALIDATE_PARENTS_EXIST = True  # check that parents are in the list of monsters that can breed
    # VALIDATE_RESULTS_EXIST = True  # check that results are in the list of monsters that can be bred

    # master sheet details
    SHEET_ID = "15kDI5lQL7szwh4YbjeZ6c4xRcLNpiMkXwLwfQzqGhCQ"
    GID = "0"

    # live fetch of the sheet as a csv
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"
    if verbose:
        print("Fetching breeding data from:", url)
    df = pd.read_csv(url, header=0)
    if verbose:
        print("Breeding data fetched")

    # monster breeding details
    VALIDATION_SHEET_ID = "1jn0Pt8SH0ve0WiH8RZlL-nyQODSriUCOJQlN6yLc9_E"
    VALIDATION_GID = "1001758888"
    url_val = f"https://docs.google.com/spreadsheets/d/{VALIDATION_SHEET_ID}/export?format=csv&gid={VALIDATION_GID}"
    if verbose:
        print("Fetching validation data from:", url_val)
    df_val = pd.read_csv(url_val, usecols=[1, 2], header=0)
    if verbose:
        print("Validation data fetched")

    all_parent_monsters = df_val['Monsters that breed'].dropna().unique().tolist()
    all_result_monsters = df_val['Monsters that are bred'].dropna().unique().tolist()
    #print(all_parent_monsters)
    #print(all_result_monsters)


    # flattening nested columns
    unnamed_col_count = 0
    for col in df.columns:
        if 'Unnamed' in col:
            prev_col = df.columns[df.columns.get_loc(col) - 1]
            df.rename(columns={col: f"{prev_col} Level"}, inplace=True)
            unnamed_col_count += 1

        # replaces newlines in column names with spaces if present
        if '\n' in col:
            df.rename(columns={col: col.replace('\n', ' ')}, inplace=True)

        # strips double quotes from column names if present
        if '"' in col:
            df.rename(columns={col: col.replace('"', '')}, inplace=True)

        if unnamed_col_count > 2:
            exit(1)  # format has changed, exit

    # renaming the old Parent 1/2 columns to Parent 1/2 Species to fit with the flattened structure
    df.rename(columns={'Parent 1': 'Parent 1 Species', 'Parent 2': 'Parent 2 Species'}, inplace=True)
    # drops the second row which is now redundant
    df = df.drop(index=0).reset_index(drop=True)

    # date validation
    if VALIDATE_MSM_DATE:
        date_col = [col for col in df.columns if 'Date' in col][0]
        if verbose:
            print(date_col)
        df = df[pd.to_datetime(df[date_col], errors='coerce').notna()].reset_index(drop=True)
        df[date_col] = pd.to_datetime(df[date_col])

    # time since reset validation or removal
    if REMOVE_TIME_SINCE_RESET:
        time_col = [col for col in df.columns if 'Time since reset' in col][0]
        df = df.drop(columns=[time_col])
    else:
        time_col = [col for col in df.columns if 'Time since reset' in col][0]
        df = df[pd.to_timedelta(df[time_col], errors='coerce').notna()].reset_index(drop=True)


    # assume zero torches coercion or removal of blank torch-count entries
    if ASSUME_ZERO_TORCHES:
        torch_col = [col for col in df.columns if 'Torches' in col][0]
        df[torch_col] = df[torch_col].fillna(0)
    else:
        torch_col = [col for col in df.columns if 'Torches' in col][0]
        df = df[pd.to_numeric(df[torch_col], errors='coerce').notna()].reset_index(drop=True)

    # parent monster validation
    if VALIDATE_PARENTS_EXIST:
        parent1_col = [col for col in df.columns if 'Parent 1 Species' in col][0]
        parent2_col = [col for col in df.columns if 'Parent 2 Species' in col][0]

        invalid_parents_df = df[~df[parent1_col].isin(all_parent_monsters) | ~df[parent2_col].isin(all_parent_monsters)]
        if not invalid_parents_df.empty:
            if verbose:
                print("Invalid parent monster entries:")
                print(invalid_parents_df)

        df = df[df[parent1_col].isin(all_parent_monsters) & df[parent2_col].isin(all_parent_monsters)].reset_index(drop=True)

    # Make M AIr be M Air
    if CHECK_M_AIR:
        df["Island"] = df["Island"].replace("M AIr", "M Air")
        # mask = df["Island"] == 'M AIr'
        # df["Island", mask] = "M Air"

    # result monster validation
    if VALIDATE_RESULTS_EXIST:
        result_col = [col for col in df.columns if 'Result Monster' in col][0]

        invalid_results_df = df[~df[result_col].isin(all_result_monsters)]
        if not invalid_results_df.empty:
            if verbose:
                print("Invalid result monster entries:")
                print(invalid_results_df)

        df = df[df[result_col].isin(all_result_monsters)].reset_index(drop=True)

    # print(df)

    df.to_csv('msm_data.csv', index=False)
    return df

def read_from_csv():
    df = pd.read_csv("msm_data.csv")
    df["Date (MSM time) (MM/DD/YYYY)"] = pd.to_datetime(df["Date (MSM time) (MM/DD/YYYY)"])
    df["Torches Lit"] = pd.to_numeric(df["Torches Lit"])
    return df

if __name__ == "__main__":
    df = read_data()
    print(df.head())