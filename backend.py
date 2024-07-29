from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from statistics import median

app = Flask(__name__)
CORS(app)

def find_min_avg_schools(block_group_ids, school_block_group_list):
    memo = {}
    
    def recursive_helper(covered, current_avg, bg_to_school):
        covered_tuple = tuple(sorted(covered))
        
        if set(covered) == set(block_group_ids):
            return [], current_avg, bg_to_school
        
        if covered_tuple in memo:
            return memo[covered_tuple]
        
        best_result = None
        best_avg = float('inf')
        best_bg_to_school = None
        
        for school in school_block_group_list:
            school_bgs = school[:-4]
            school_name = school[-4]
            avg_distance = school[-1]
            
            new_covered = list(set(covered + school_bgs))
            new_bg_to_school = bg_to_school.copy()
            for bg in school_bgs:
                new_bg_to_school[bg] = school_name

            if len(new_covered) > len(covered):
                result, new_avg, new_bg_to_school = recursive_helper(new_covered, avg_distance, new_bg_to_school)
                
                if best_result is None or len(result) + 1 < len(best_result) or (len(result) + 1 == len(best_result) and new_avg < best_avg):
                    best_result = result + [school_name]
                    best_avg = new_avg
                    best_bg_to_school = new_bg_to_school
        
        memo[covered_tuple] = (best_result, best_avg, best_bg_to_school)
        return best_result, best_avg, best_bg_to_school
    
    min_schools, min_avg, bg_to_school = recursive_helper([], float('inf'), {})
    return min_schools, min_avg, bg_to_school

def find_min_medians_schools(block_group_ids, school_block_group_list):
    memo = {}
    
    def recursive_helper(covered, current_median, bg_to_school):
        covered_tuple = tuple(sorted(covered))
        
        if set(covered) == set(block_group_ids):
            return [], current_median, bg_to_school
        
        if covered_tuple in memo:
            return memo[covered_tuple]
        
        best_result = None
        best_median = float('inf')
        best_bg_to_school = None
        
        for school in school_block_group_list:
            school_bgs = school[:-4]
            school_name = school[-4]
            median_distance = school[-2]
            
            new_covered = list(set(covered + school_bgs))
            new_bg_to_school = bg_to_school.copy()
            for bg in school_bgs:
                new_bg_to_school[bg] = school_name

            if len(new_covered) > len(covered):
                result, new_median, new_bg_to_school = recursive_helper(new_covered, median_distance, new_bg_to_school)
                
                if best_result is None or len(result) + 1 < len(best_result) or (len(result) + 1 == len(best_result) and new_median < best_median):
                    best_result = result + [school_name]
                    best_median = new_median
                    best_bg_to_school = new_bg_to_school
        
        memo[covered_tuple] = (best_result, best_median, best_bg_to_school)
        return best_result, best_median, best_bg_to_school
    
    min_schools, min_median, bg_to_school = recursive_helper([], float('inf'), {})
    return min_schools, min_median, bg_to_school

def find_min_total_distance_schools(block_group_ids, school_block_group_list):
    memo = {}
    
    def recursive_helper(covered, bg_to_school):
        covered_tuple = tuple(sorted(covered))
        
        if set(covered) == set(block_group_ids):
            return [], 0, bg_to_school
        
        if covered_tuple in memo:
            return memo[covered_tuple]
        
        best_result = None
        best_distance = float('inf')
        best_bg_to_school = None
        
        for school in school_block_group_list:
            school_bgs = school[:-4]
            school_name = school[-4]
            total_distance = school[-3]
            
            new_covered = list(set(covered + school_bgs))
            new_bg_to_school = bg_to_school.copy()
            for bg in school_bgs:
                new_bg_to_school[bg] = school_name

            if len(new_covered) > len(covered):
                result, new_distance, new_bg_to_school = recursive_helper(new_covered, new_bg_to_school)
                new_distance += total_distance
                
                if best_result is None or len(result) + 1 < len(best_result) or (len(result) + 1 == len(best_result) and new_distance < best_distance):
                    best_result = result + [school_name]
                    best_distance = new_distance
                    best_bg_to_school = new_bg_to_school
        
        memo[covered_tuple] = (best_result, best_distance, best_bg_to_school)
        return best_result, best_distance, best_bg_to_school
    
    min_schools, min_distance, bg_to_school = recursive_helper([], {})
    return min_schools, min_distance, bg_to_school

@app.route('/nearest_schools', methods=['POST'])
def nearest_schools():

    # read xlsx file
    Geocoded_Georgia_high_schools_df = pd.read_excel('Geocoded_Georgia_high_schools.xlsx')
    block_group_id_nearest_school = pd.read_json('block_group_id_nearest_school.json', typ='series')

    block_groups_df = pd.read_excel('block_groups_df.xlsx')

    # read the block_group_school_distance json file
    block_group_school_distance = pd.read_json('block_group_school_distance.json', typ='series')

    # print(block_group_school_distance[1])

    # Get the block group ids from the request
    block_group_ids = request.json['block_group_ids']

    # Get the distance from the request
    input_distance = request.json['distance']

    criteria = request.json.get('criterion')

    # convert the distance to a number
    input_distance = float(input_distance)

    # print(block_group_ids)
    
    #convert the block group ids to numbers
    block_group_ids = [int(block_group_id) for block_group_id in block_group_ids]

    # Filter block_group_school_distance to include only the block groups sent from frontend
    # filtered_block_group_school_distance = {block_id: block_group_school_distance[block_id] for block_id in block_group_ids if block_id in block_group_school_distance}
    
    # print(filtered_block_group_school_distance.get(block_group_ids[0]))
    # Find the nearest schools for each block group


    # Filter block_group_school_distance to include only the block groups sent from frontend
    filtered_block_group_school_distance = {
        block_id: dict(sorted(block_group_school_distance[block_id].items(), key=lambda item: item[1]))
        for block_id in block_group_ids if block_id in block_group_school_distance
    }
    #print(filtered_block_group_school_distance.get(block_group_ids[1]))

    # remove all the schools whose distance is greater than the distance requested
    for block_id in filtered_block_group_school_distance:
        filtered_block_group_school_distance[block_id] = {
            school: distance
            for school, distance in filtered_block_group_school_distance[block_id].items()
            if distance <= input_distance
        }
    # print(filtered_block_group_school_distance) 

    # store the first school name which is common to all the block groups. If a block group does not have a common school then store the 1st school name for that block group
    # block_group_id_nearest_school = {}
    # for block_id in filtered_block_group_school_distance:
    #     if len(filtered_block_group_school_distance[block_id]) > 0:
    #         block_group_id_nearest_school[block_id] = list(filtered_block_group_school_distance[block_id].keys())[0]
    #     else:
    #         block_group_id_nearest_school[block_id] = filtered_block_group_school_distance[block_id].get(0)
    # print(block_group_id_nearest_school)

    # insert the schools in the hashmap, schools will be the key and value as list of block group id's
    school_block_group = {}
    for block_id in filtered_block_group_school_distance:
        for school in filtered_block_group_school_distance[block_id]:
            if school in school_block_group:
                school_block_group[school].append(block_id)
            else:
                school_block_group[school] = [block_id]

    #print(school_block_group)

   # Create a list from the school_block_group map, where the key is followed by values in each list
    school_block_group_list = []
    for school, block_ids in school_block_group.items():
        #print(block_ids)
        # Create a list with all block_ids followed by the school name
        temp_list = block_ids + [school]
        school_block_group_list.append(temp_list)
    
    # print(school_block_group_list)

    # Sort the list based on its length
    school_block_group_list.sort(key=len, reverse=True)
    # print(school_block_group_list)

    # for each list in school_block_group_list, 

    # for the above school_block_group_list, for each list find the aggregate of distance between the schools and the block groups in the list and append at the end of each list
    for school_list in school_block_group_list:
        distance_sum = 0
        for block_id in school_list[:-1]:
            distance_sum += filtered_block_group_school_distance[block_id][school_list[-1]]
        school_list.append(distance_sum)

       # for each list find average distance from the schools to the block groups in the list and append at the end of each list
        distance_avg = distance_sum / len(school_list[:-2])
        school_list.append(distance_avg)

    # for the above school_block_group_list, find the median of the distance between the schools and the block groups in the list and append at the end of each list
    for school_list in school_block_group_list:
        distance_list = [filtered_block_group_school_distance[block_id][school_list[-3]] for block_id in school_list[:-3]]
        distance_list.sort()
        distance_median = distance_list[len(distance_list) // 2]
        school_list.append(distance_median)

    print("school_block_group_list: ",school_block_group_list)
    
    # Work on the below code Start [878, 879, 'Waynesville Primary School', total: 19.14412519212606,avg:9.57206259606303,median:12.102128245285268]
    
    result = []
    covered_block_ids = set()

    # [232, 421, 'Paul D. West Middle School', 11.357044255181256, 5.678522127590628, 9.969667536634615]
    # find minimum number of lists from school_block_group_list such that all the input block groups are covered

    for school_list in school_block_group_list:
        school_name = school_list[-4]
        block_ids = set(school_list[:-4])
    
        # Check if this school covers any new block group IDs
        if not covered_block_ids.issuperset(block_ids):
            result.append(school_name)  # Append the school name
            covered_block_ids.update(block_ids)  # Add the block IDs to the covered set
    
        # If all block group IDs are covered, break the loop
        if covered_block_ids.issuperset(block_group_ids):
            break

    # print(result)
      # Find the minimal set of schools for different criteria
    optimal_schools, min_distance, bg_to_school_total = find_min_total_distance_schools(block_group_ids, school_block_group_list)
    print(f"Optimal Schools (Total Distance): {optimal_schools}")
    print(f"Minimum Total Distance: {min_distance}")

    optimal_schools, min_median, bg_to_school_median = find_min_medians_schools(block_group_ids, school_block_group_list)
    print(f"Optimal Schools (Median Distance): {optimal_schools}")
    print(f"Minimum Median Distance: {min_median}")

    optimal_schools, min_avg, bg_to_school_avg = find_min_avg_schools(block_group_ids, school_block_group_list)
    print(f"Optimal Schools (Average Distance): {optimal_schools}")
    print(f"Minimum Average Distance: {min_avg}")

    # Determine the closest schools for block groups based on the desired metric
    if criteria == 'total_distance':
        bg_to_school = bg_to_school_total
    elif criteria == 'median_distance':
        bg_to_school = bg_to_school_median
    else:
        bg_to_school = bg_to_school_avg
    
    print("Closest school based on metric",bg_to_school)
    ## find minimum number of lists from school_block_group_list which contains all the input block groups and with minimum 
    # optimal_schools, total_distance = find_min_total_distance_schools(block_group_ids, school_block_group_list)
    # print("Schools: ",optimal_schools)
    # print("Total Distance: ",total_distance)
    # # optimal_schools, min_median, min_avg = find_min_median_schools(block_group_ids, school_block_group_list)
    # # print(f"Optimal Schools: {optimal_schools}")
    # # print(f"Minimum Aggregate Median Distance: {min_median}")
    # # print(f"Minimum Aggregate Average Distance: {min_avg}")

    # # Find the minimal set of schools
    # optimal_schools, min_median = find_min_medians_schools(block_group_ids, school_block_group_list)
    # print(f"Optimal Schools: {optimal_schools}")
    # print(f"Minimum Median Distance: {min_median}")

    # # Find the minimal set of schools
    # optimal_schools, min_avg = find_min_avg_schools(block_group_ids, school_block_group_list)
    # print(f"Optimal Schools: {optimal_schools}")
    # print(f"Minimum Average Distance: {min_avg}")

    final_closest_schools = []
    # for school in result:
    #     school_info = Geocoded_Georgia_high_schools_df[Geocoded_Georgia_high_schools_df['USER_Sch_2'] == school]
    #     school_info = school_info.to_dict(orient='records')[0]
    #     final_closest_schools.append(school_info)
    
    # print(final_closest_schools)
    for block_id in block_group_ids:
        if block_id in bg_to_school:
            school_info = Geocoded_Georgia_high_schools_df[Geocoded_Georgia_high_schools_df['USER_Sch_2'] == bg_to_school[block_id]]
            school_info = school_info.to_dict(orient='records')[0]
            final_closest_schools.append(school_info)

    
    # Extract longitude and latitude for each block group ID
    block_group_locations = []
    for block_id in block_group_ids:
        block_group = block_groups_df[block_groups_df['block_group_id'] == block_id]
        if not block_group.empty:
            block_group_info = {
                'block_group_id': block_id,
                'longitude': block_group['INTPTLON'].values[0],
                'latitude': block_group['INTPTLAT'].values[0]
            }
            block_group_locations.append(block_group_info)

    # Extract the longitude and latitude for each school in the final_closest_schools list
    school_locations = []
    for school in final_closest_schools:
        school_info = {
            'school': school['USER_Sch_2'],
            'longitude': school['X'],
            'latitude': school['Y']
        }
        school_locations.append(school_info)
    
    response = {
        'block_group_locations': block_group_locations,
        'school_locations': school_locations,
        'block_id_to_school': bg_to_school
    }


    return jsonify(response)
    # nearest_schools = []
    # for block_id in block_group_ids:
    #     if block_id in block_group_id_nearest_school:
    #         nearest_school = block_group_id_nearest_school[block_id]
    #         nearest_schools.append(nearest_school)
    #     else:
    #         nearest_schools.append(None)
    
    # # Create a DataFrame to store the results
    # nearest_schools_df = pd.DataFrame({'block_group_id': block_group_ids, 'nearest_school': nearest_schools})
    
    # # Add the latitude and longitude of the schools
    # nearest_schools_df['School_longitude'] = None
    # nearest_schools_df['School_latitude'] = None
    # for i, row in nearest_schools_df.iterrows():
    #     school = Geocoded_Georgia_high_schools_df[Geocoded_Georgia_high_schools_df['USER_Sch_2'] == row['nearest_school']]
    #     nearest_schools_df.at[i, 'School_longitude'] = school['X'].values[0]
    #     nearest_schools_df.at[i, 'School_latitude'] = school['Y'].values[0]
    
    # # Add the latitude and longitude of the block groups
    # nearest_schools_df['Block_group_longitude'] = None
    # nearest_schools_df['Block_group_latitude'] = None
    # for i, row in nearest_schools_df.iterrows():
    #     block_group = block_groups_df[block_groups_df['block_group_id'] == row['block_group_id']]
    #     nearest_schools_df.at[i, 'Block_group_longitude'] = block_group['INTPTLON'].values[0]
    #     nearest_schools_df.at[i, 'Block_group_latitude'] = block_group['INTPTLAT'].values[0]
    
    # return jsonify(nearest_schools_df.to_dict(orient='records'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)