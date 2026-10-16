from search import vetorial_search_prompt, llm_interaction

def main():
    userQuestion = "xuxu"

    vetorial_search_prompt(userQuestion)

    results = vetorial_search_prompt(userQuestion)

    llmAnswer = llm_interaction(contexto=results, pergunta=userQuestion)

    print("Resposta do modelo:")
    print(llmAnswer.content[0].get('text', ''))

if __name__ == "__main__":
    main()