import json
from dotenv import load_dotenv, find_dotenv
from typing import List
from pydantic import BaseModel, Field
from docx import Document
from openai import OpenAI
import instructor

from prompts import EXTRACT_BY_CHUNK_ONLY_ENTITIES_PROMPT

load_dotenv(find_dotenv())


class Condition(BaseModel):
    term_name: str = Field(
        description="Name of condition, rule or fact described in the document"
    )
    term_value: str = Field(
        description="Value of condition, rule or fact described in the document, corresponding to `term_name`"
    )
    contract_section: str = Field(
        description="Clause number in which the condition / term is located"
    )


class Response(BaseModel):
    conditions: List[Condition] = Field(
        description="Set of all important rules, conditions or facts found in the document"
    )


def word_to_str(path: str):
    doc = Document(path)
    all_text = []
    # split by rows
    for docpara in doc.paragraphs:
        all_text.append(docpara.text)
    # split by paragraphs
    full_text = "\n".join(all_text)
    splitted_paragraphs = full_text.split("\n\n")
    # remove empty chunks
    splitted_paragraphs = [el for el in splitted_paragraphs if len(el) > 0]
    # merge two subsequent chunks if very short (usually - headings)
    final_chunks = []
    cur_chunk = ""
    for row in splitted_paragraphs:
        if len(row) < 250:
            cur_chunk += "\n" + row
        else:
            if cur_chunk != "":
                final_chunks.append(cur_chunk)
                cur_chunk = ""
            final_chunks.append(row)
    if cur_chunk != "":
        final_chunks.append(cur_chunk)
    return final_chunks


def extract(doc_chunk: str):
    # Apply the patch to the OpenAI client
    client = instructor.from_openai(OpenAI())
    entities: Response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0.1,
        response_model=Response,
        max_retries=3,
        messages=[
            {
                "role": "user",
                "content": EXTRACT_BY_CHUNK_ONLY_ENTITIES_PROMPT.format(
                    document=doc_chunk
                ),
            }
        ],
    )
    return entities


def extract_from_chunk(chunks: List[str], doc_name: str):
    entities = []
    for i, chunk in enumerate(chunks):
        chunk_entities = extract(chunk)
        chunk_entities = chunk_entities.model_dump()["conditions"]
        for ent in chunk_entities:
            ent["source"] = doc_name
            entities.append(ent)
    return entities


def full_extraction(path_to_file: str):
    splitted_paragraphs = word_to_str(path_to_file)
    # split on 2 documents
    second_doc_name = "Amendment to the Service Agreement Regarding Travel Expenses"
    amendment_chunk_start = [
        (i, el) for i, el in enumerate(splitted_paragraphs) if second_doc_name in el
    ][0]
    start_pos_in_chunk = (
        amendment_chunk_start[1].strip().replace("\n\n", "").find(second_doc_name)
    )
    service_agreement_chunks = splitted_paragraphs[: amendment_chunk_start[0]]
    amendment_chunks = splitted_paragraphs[amendment_chunk_start[0] + 1 :]
    if start_pos_in_chunk != 0:
        # split chunk on 2 parts and add each part to corresponding neighbour chunks
        service_agreement_chunks.append(amendment_chunk_start[1][:start_pos_in_chunk])
        amendment_chunks.insert(0, amendment_chunk_start[1][start_pos_in_chunk:])
    else:
        amendment_chunks.insert(0, amendment_chunk_start[1])

    # run extraction
    all_entities = extract_from_chunk(
        chunks=service_agreement_chunks, doc_name="Contract"
    )
    all_entities.extend(
        extract_from_chunk(chunks=amendment_chunks, doc_name="Amendment")
    )
    return all_entities


if __name__ == "__main__":
    ### Solution 2 - extract entities by chunks, hard code separation of contracts
    all_entities = full_extraction(
        path_to_file="data/Contract + Amendment example v3 .docx"
    )
    with open("data/extracted_entities_final.json", "w") as f:
        json.dump(all_entities, f)

    ### Solution 1 - extract entities and contract name at the same time by chunks
    # splitted_paragraphs = word_to_str("data/Contract + Amendment example v3 .docx")
    # chain = get_extractor(prompt_name=EXTRACT_BY_CHUNK_AND_FULL_CONTEXT_PROMPT)
    # all_entities = []
    # for i, chunk in enumerate(splitted_paragraphs):
    #     context = '' if i == 0 else "\n".join(splitted_paragraphs[:i])
    #     print(f"chunk {chunk}")
    #     chunk_entities = chain.invoke({"document": chunk, "context": context})
    #     all_entities.extend(chunk_entities)
    # with open("data/extracted_entities.json", "w") as f:
    #     json.dump(all_entities, f)
