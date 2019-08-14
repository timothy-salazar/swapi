from data_analysis import web_utilities, df_utilities

main():
    base_url = 'http://swapi.co/api/people/'
    column_list = ['name','birth_year','eye_color','gender','hair_color',
                    'height','mass','skin_color','homeworld']
    df = df_utilities.get_initial_df(column_list)
    people_resource = get_json(base_url)
    other_stuff(people_resource)




if __name__ == '__main__':
    main()
