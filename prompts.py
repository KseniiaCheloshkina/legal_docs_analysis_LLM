EXTRACT_BY_CHUNK_AND_FULL_CONTEXT_PROMPT = """
You are very attentive lawyer and expert in legal documents analysis.
Your goal is to help me to understand the terms of contract by extracting the important entities mentioned in the text of contract.
I have a file where several contracts are presented, one by one. So you are given all the text from the beginning of the file between <Context> and </Context>, and the text of contract under examination - given between <Document> and </Document>.
All the dates, time periods, names, sums are important to me, that's why do your best to extract them all. This is very important to my career.
To complete this task follow the next workflow:
1. Identify, which information from the <Document> section could be important to me.
2. Extract this information from <Document> block and pack it into JSON with keys "term_name" and "term_value", like here: 
[{{"term_name": "term_name_1", "term_value": "term_value_1"}}, {{"term_name": "term_name_2", "term_value": "term_value_2"}}, ...]
Rules:
- to create term name, use 1 to 3 words. If possible - try to use these which are presented in a row in the original document with exception of propositions and articles (ex. "start date of the agreement is 21 of february 2023" -> "start_date_agreement"). Otherwise use words in term name only from the text.
- put term value into your answer by extracting piece of text from document - do not apply any kind of formatting! Only extract piece of text (ex. value of term "start_date_agreement" in document "start date of the agreement is 21 of february 2023" - "21 of february 2023"). Each entity value should 1-5 words. Try to make it as short as possible but dont miss words changing the meaning of term.
- if you dont know the value of entity, dont add it into final list. NEVER add items with placeholders like `insert date here`
- use <Context> block only for your understanding, do not extract entities from <Context>. Extract entities only from <Document> block.
3. To enable me to verify your work, add to every term its exact location in the document using document hierarchy by specifying the item number.
To do it, you can use information from the previous document blocks (given between <Context> and </Context>).
You have to add keys:
- "contract_name" (name of current contract or full name of amendment to a contract, always given in the <Context> block). Should be one of "Service Agreement" or "Amendment to the Service Agreement Regarding Travel Expenses". Check carefully, to which contract (contract itself or amendment) an entity belongs to.
- "contract_section" (clause number of contract, where the entity is located). Use as precise clause number as possible (ex. "3.2" is better than "3", if the entity is right after "3.2" label). For the entities which do not belong to any numbered block of text, you can mark as `beginning` or `final notes` depending on the context and content of the document.
Follow the next format:
{{"term_name": "term_name_1", "term_value": "term_value_1"}} -> {{"term_name": "term_name_1", "term_value": "term_value_1", "contract_name": "<contract name>", "contract_section": "<entity clause number>"}}
where <entity clause number> is extracted from text (like '1.1' or '2.3' - as precise as possible) or if there are no such designations - as `beginning` or `final notes`.
4. Before responding, make sure, that all terms are extracted, their values are correct and locations inside the document are correct.

### Examples
Example 1
<Context> Service Agreement, signed between </Context>
<Document> “Black Inc." (with Black Erich as CEO), hereinafter referred to as the “Client,” and “LLC White” (with White Amanda as CEO), hereinafter referred to as the “Contractor”. </Document>
Output:
[
    {{"term_name": "client_company_name", "term_value": "Black Inc.", "contract_name": "Service Agreement", "contract_section": "beginning"}},
    {{"term_name": "client_ceo", "term_value": "Black Erich", "contract_name": "Service Agreement", "contract_section": "beginning"}},
    {{"term_name": "contractor_company_name", "term_value": "LLC White", "contract_name": "Service Agreement", "contract_section": "beginning"}},
    {{"term_name": "contractor_ceo", "term_value": "White Amanda", "contract_name": "Service Agreement", "contract_section": "beginning"}},
]
Example 2
<Context> Service Agreement, signed between
“Black Inc." (with Black Erich as CEO), hereinafter referred to as the “Client,” and “LLC White” (with White Amanda as CEO), hereinafter referred to as the “Contractor”. 
</Context>
<Document> 1.1. Object of the Agreement: The Contractor agrees to provide cleaning services. </Document
Output:
[{{"term_name": "services", "term_value": "cleaning", "contract_name": "Service Agreement", "contract_section": "1.1."}}]

Example 3
<Context> Service Agreement, signed between
“Black Inc." (with Black Erich as CEO), hereinafter referred to as the “Client,” and “LLC White” (with White Amanda as CEO), hereinafter referred to as the “Contractor”. 
1.1. Object of the Agreement: The Contractor agrees to provide cleaning services.
</Context>
<Document> 1.2. Start date of the agreement: 23.06.2022 </Document
Output:
[{{"term_name": "start_date_agreement", "term_value": "23.06.2022", "contract_name": "Service Agreement", "contract_section": "1.2."}}]

### Input
<Context> {context} </Context>
<Document> {document} </Document>
Output:
"""

EXTRACT_BY_CHUNK_ONLY_ENTITIES_PROMPT = """
You are very attentive lawyer and expert in legal documents analysis, and also - perfect entity extraction system.
Your goal is to help me to understand the terms of contract by extracting conditions mentioned in the text of contract. This is very important to my career.
To complete this task follow the next workflow:
1. Identify, which conditions are presented in the text of contract. I dont need hypothetical examples and only need to extract facts and rules (conditions).
2. Extract this information and pack it into JSON with keys "term_name" and "term_value", like here: 
[{{"term_name": "term_name_1", "term_value": "term_value_1"}}, {{"term_name": "term_name_2", "term_value": "term_value_2"}}, ...]
Rules:
- to create term name, use 1 to 3 words. If possible - try to use these which are presented in a row in the original document with exception of propositions and articles (ex. "start date of the agreement is 21 of february 2023" -> "start_date_agreement"). Otherwise use words in term name only from the text.
- put term value into your answer by extracting piece of text from document - do not apply any kind of formatting! Only extract piece of text (ex. value of term "start_date_agreement" in document "start date of the agreement is 21 of february 2023" - "21 of february 2023"). 
- Each `term_value` should contain only 1-5 words. Try to make it as short as possible but dont miss words changing the meaning of term.
- if you dont know the value of entity, dont add it into final list
- Do not add as terms some hypothetical examples given in the contract - only extract conditions (rules). For example, from phrase "if you are traveling to London, the limit is 1000$" you need to extract "London_traveling_limit": "1000$" but not the "travel_destination": "London" (because its hypothetical situation given to demonstrate rule of London traveling limit, but by this contract I'm not obliged to travel to London).
- Do not extract entities from `example` section
3. To enable me to verify your work, add to every term its exact location in the document using document hierarchy by specifying the clause number.
To do so add key "contract_section" to each entity JSON, use as precise clause number as possible (ex. "3.2" is better than "3", if the entity is right after "3.2" label). 
Follow the next format:
{{"term_name": "term_name_1", "term_value": "term_value_1"}} -> {{"term_name": "term_name_1", "term_value": "term_value_1", "contract_section": "<entity clause number>"}}
where <entity clause number> is extracted from text (like '1.1' or '2.3' - as precise as possible). For the entities which do not belong to any numbered block of text, you can mark as `common_terms`.
(ex. "1.2. Start date of the agreement is 21 of february 2023" -> {{"term_name": "start_date_agreement", "term_value": "21 of february 2023", "contract_section": "1.2."}})
4. Before responding, make sure that all conditions are extracted, their values and locations inside the document are correct. 
- Check that the entity reflects the rule, and does not extracted from some specific example. 
- Make sure that entity value has a meaningful information and do not repeat almost all words from term name (like {{"term_name":"necessary_info", "term_value": "all_necessary_info"}})
- Make sure that `term_value` is not longer than 5 words, otherwise make it shorter (split on several terms or leave only most important information)

### Examples
Example 1
<Document> “Black Inc." (with Black Erich as CEO), hereinafter referred to as the “Client,” and “LLC White” (with White Amanda as CEO), hereinafter referred to as the “Contractor”. </Document>
Output:
[
    {{"term_name": "client_company_name", "term_value": "Black Inc.", "contract_section": "common_terms"}},
    {{"term_name": "client_ceo", "term_value": "Black Erich",  "contract_section": "common_terms"}},
    {{"term_name": "contractor_company_name", "term_value": "LLC White", "contract_section": "common_terms"}},
    {{"term_name": "contractor_ceo", "term_value": "White Amanda", "contract_section": "common_terms"}},
]
Example 2
<Document> 1.1. Object of the Agreement: The Contractor agrees to provide cleaning services. </Document
Output:
[{{"term_name": "services", "term_value": "cleaning", "contract_section": "1.1."}}]

Example 3
<Document> 1.3. Payment fee is 56 USD </Document
Output:
[{{"term_name": "payment_fee", "term_value": "56 USD", "contract_section": "1.3."}}]

### Input
<Document> {document} </Document>
Output:
"""

GET_CONTRACT_NAME_PROMPT = """You are perfect document analysis system. 
You are given full document text between <Document> and </Document>. It consists of 2 documents (sections) - Service Agreement and Amendment to the Service Agreement Regarding Travel Expenses.
Also you are given terms, earlier extracted from one of these two documents.
Your goal is to carefully check whether the entity, described between <Entity> and </Entity> is presented in one of the contracts (you have to find it in the document) and
 - If you cant find the entity in the document - respond with 'ABSENT'
- If entity is presented in Service Agreement section (after 'Service Agreement' heading abd before 'Amendment to the Service Agreement Regarding Travel Expenses' heading) - respond with `SERVICE_AGREEMENT`
- If entity is presented in Amendment to the Service Agreement Regarding Travel Expenses (after 'Amendment to the Service Agreement Regarding Travel Expenses' heading) - respond with `AMENDMENT_SERVICE_AGREEMENT`
- If it's presented in both, respond with `SERVICE_AGREEMENT`

<Entity> {entity} </Entity>
<Document> {document} </Document>
"""


COT_LIMITS_PROMPT = """Answer the following questions as best you can. You have access to the following tools:

{tools}

Final answer should be presented in this way: <travel_limit_sum>, because <calculation and reasoning>
For reasoning follow these steps:
1 - Find the expenses limit for single trip
2 - Search for different multipliers that could be applied for current trip based on its description (take into consideration location and time of travel)
3 - Apply multipliers to base sum to get final travel limit (like 2500 * 1.3)

To get the final answer use the following format:
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

# Example:
Question: an urgent business travel to New York City over New Year’s weekend, with flight booking required on a Friday night
Thought: what multipliers should be implied
Action: search_travel_budget_rules
Action Input: the trip is urgent travel to New York City over New Year’s weekend
Observation:  any single trip must not exceed USD 2,500, Urgency Multiplier for last-minute booking: 1.3
Thought: what multipliers should be applied to base budget of USD 2,500
Action: search_travel_budget_rules
Action Input: flight booking required on a Friday night
Observation:  Night and Weekend Travel Multiplier: 1.1 could be applied
Thought: what other multipliers could be implied
Action: search_travel_budget_rules
Action Input:  travel to New York City over New Year’s weekend
Observation: Seasonal and Location Adjustment for New York during New Year: 1.2 could be applied
Thought: what other multipliers should be implied
Action: search_travel_budget_rules
Action Input: all is taken into account
Observation: no more multipliers
Thought: I now know the final answer
Final Answer: $4158, because $2500 * 1.1 (Night and Weekend Travel Multiplier) * 1.2 (Seasonal and Location Adjustment) * 1.3 (Urgency Multiplier) = $4158

Begin!

Question: {input}
Thought:{agent_scratchpad}
"""

QUESTION = "Calculate budget for my next travel: {conditions}"
