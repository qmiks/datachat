def main():
    import streamlit as st

    st.title("Welcome to Data Chat!")
    
    user_input = st.text_input("You:")
    
    if st.button("Send"):
        if user_input.lower() in ['exit', 'quit']:
            st.write("Exiting Data Chat. Goodbye!")
        else:
            response = handle_user_input(user_input)
            st.write("DataChat:", response)

def handle_user_input(user_input):
    return "This is a placeholder response."

if __name__ == "__main__":
    main()