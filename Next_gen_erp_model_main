# getting the user input first and then 
class chat_bot:
    
    def __init__(self):
        self.user_inpt_create_tbl=None
        self.user_inpt_add_data=None
        self.user_inpt_normal=None # this is to ask user whether they want to create column of add data

    
    def calling_the_model(self): # fun to call the initial model
        
        
        prompt = ChatPromptTemplate(
            messages=[
                SystemMessagePromptTemplate.from_template(
                    "You are a chatter accountant chatbot, having conversation with human."
                ),
                MessagesPlaceholder(variable_name="chat_history"),
                HumanMessagePromptTemplate.from_template("{question}"),
            ]
        )
        #this is to initiate memory for the chat bot so it can recall the prior chat history and give answer
        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        conversation = LLMChain(llm=llm, prompt=prompt, verbose=True, memory=memory)
        

    def model_getcolumns_prompt_initialization(self):
        print("<<<<< call the model successfully >>>")
        self.calling_the_model()
        result = conversation({"question": '''you are a good chat model who follows user instruction,
            if the user gave you instruction such as, "create a columns with name like menu, price,quantity,date" or 
            "create a table menu, price,quantity,date" or "table create menu, price,quantity,date"
            then you have to give me the output as such "The column names I have created for the table are:1. tea_menu2. price3. date4. gst " always
            follow this out " The column names I have created for the table are:1. tea_menu2. price3. date4. gst " , you won't use any word in between like "and",
            just follow this format "The column names I have created for the table are:1. tea_menu2. price3. date4. gst"'''}, True)

    def model_getdata_prompt_nitialization(self):
        print(" <<<<< getting model data successfully >>>>> ")
        result=conversation(
            {"question": '''now what I want is that whenever the user says add these items to data, for example if user says "add momo to name, 
            add 50 price, 3 quantity" or  lets say the user say it like that, "add momo to name columns, 
            add 50 price columns and 3 to quantity columns" then you have to simple give me the name of the columns and there value in dict format, 
            for example like this {name: "momo" ,price : 50 ,quantity : 3} always follow this format, the user may say in different way,
            with variety of product no only momo, so you have to understand it, and give me the output in the format I mentioned '''},True)
 
    def get_user_clms(self): #now after initial prompt we will ask the user to give the prompt 
        self.model_getcolumns_prompt_initialization()
        
        #asking to create a table and then we are formating the table and gettig the columns name which the user mentioned
        result=conversation(
            {"question": input('give me your columns name :')},True) #here i have used input but you can give direct prompt here.
        # Check if 'text' key exists in the result dictionary
        if 'text' in result:
            # Remove newline characters from the 'text' value
            cleaned_paragraph = result['text'].replace('\n', '')
            patter1= r"(\d+\.+\s+([a-z_]+))"
            matches = re.findall(patter1, cleaned_paragraph)
            extracted_column_names = [match[1] for match in matches]
            print(extracted_column_names)
        
        else:
            print("No 'text' found in the result.")
    
    #now here we will add the adding code
    def get_user_data(self):
        self.model_getcolumns_prompt_initialization() # giving the prompt on how to give the columns and then we are passing the get data prompt
        self.model_getdata_prompt_nitialization() # getting the user data 
        # Check if 'text' key exists in the result dictionary
        result=conversation({"question": input('give me your data :')},True)
        if 'text' in result:           
            cleaned_paragraph = result['text'].replace('\n', '')
            pattern = r"(\{+([a-z_]+)\:([^\}]+)\})"  # Capture key and value separately   
            # Find all matches
            matches = re.findall(pattern, cleaned_paragraph)
            # Extract column names and values
            extracted_data = {}
            for match in matches:
                key, value = match[1], match[2]  # Group 1 is the key, Group 2 is the value
                extracted_data[key] = value.strip('"')  # Remove potential quotation marks
        
            print(extracted_data)  # Output: {'name': 'Arjun', 'price': '40', 'gst_list': '2'}
                   
    def ask_user(self):
        
        while True:           
            #ask the user wheter they want to create a colm or add data
            ask_user=input('enter C to create colunmns name | enter A to add data ').lower()
            if ask_user == 'q':
                pass
            if ask_user == "c":
                self.create_user_clms() # func to get the user culms
            elif ask_user == "a":
                self.get_user_data() # func get the user data
            else :
                print('Given wrong input try again.')
