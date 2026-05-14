import operator
import re
from typing import Annotated, Sequence, TypedDict

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, END

from core.rag import query_rag
from levels.l0_commander import L0Commander

# Configuration du LLM (Ollama)
llm = ChatOllama(model="llama3.2:1b", temperature=0)

# ==========================================
# 1. Définition des Actions Directes (Outils)
# ==========================================

commander_system = L0Commander()

def calculate_expression(expression: str) -> str:
    """Outil mathématique pour évaluer des calculs ou équations."""
    # Nettoyage de base pour la sécurité
    allowed = set("0123456789+-*/(). ")
    cleaned = "".join(c for c in expression if c in allowed)
    try:
        return str(eval(cleaned))
    except Exception as e:
        return f"Erreur de calcul: {e}"

# ==========================================
# 2. Création des Agents (Nodes) à exécution directe
# ==========================================
# Pour les petits modèles (1B), l'exécution directe est plus robuste que le ReAct JSON.

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next_node: str

def router_node(state: AgentState):
    """
    Agent Routeur (Orchestration Conditionnelle) :
    Analyse la demande et décide vers quel agent l'envoyer.
    """
    last_msg = state["messages"][-1].content.lower()
    
    # Logique de routage
    if any(k in last_msg for k in ["open", "time", "cmd", "lance", "ouvre"]):
        next_node = "commander"
    elif any(k in last_msg for k in ["calculate", "math", "+", "-", "*", "calcul"]):
        next_node = "mathematician"
    elif any(k in last_msg for k in ["sofia", "projet", "rag", "agent", "connaissance"]):
        next_node = "researcher"
    else:
        next_node = "writer"
        
    print(f"\n[Orchestrateur LangGraph] Routage de la tâche vers l'agent : {next_node.upper()}")
    return {"next_node": next_node}

def run_researcher(state: AgentState):
    print("[Chercheur] Interrogation du RAG en cours...")
    query = state["messages"][-1].content
    result = query_rag(query)
    return {"messages": [AIMessage(content=f"[Informations du RAG] :\n{result}")], "next_node": "writer"}

def run_commander(state: AgentState):
    query = state["messages"][-1].content
    result = commander_system.match_and_execute(query) or "Commande non reconnue."
    return {"messages": [AIMessage(content=f"[Résultat Système] : {result}")], "next_node": "writer"}

def run_mathematician(state: AgentState):
    query = state["messages"][-1].content
    result = calculate_expression(query)
    return {"messages": [AIMessage(content=f"[Résultat Mathématique] : {result}")], "next_node": "writer"}

def writer_node(state: AgentState):
    """
    Agent Rédacteur (Orchestration Séquentielle) :
    Formate la réponse finale pour l'utilisateur.
    """
    context_messages = [m for m in state["messages"] if isinstance(m, AIMessage)]
    user_msg = state["messages"][0].content
    
    if context_messages:
        last_agent_response = context_messages[-1].content
        prompt = (
            "Tu es S.O.F.I.A, un assistant vocal intelligent.\n"
            f"L'utilisateur a demandé : '{user_msg}'\n"
            f"Résultat du système : '{last_agent_response}'\n"
            "Rédige une réponse très courte et naturelle. "
            "Si le système indique que la commande n'est pas reconnue ou a échoué, dis simplement 'Désolé, je ne trouve pas cette application' sans faire de longs discours."
        )
        response = llm.invoke([HumanMessage(content=prompt)])
        return {"messages": [AIMessage(content=response.content)], "next_node": END}
    else:
        # Conversational fallback
        response = llm.invoke(state["messages"])
        return {"messages": [response], "next_node": END}

# ==========================================
# 3. Construction du Graphe (LangGraph)
# ==========================================
workflow = StateGraph(AgentState)

# Ajout des noeuds (agents)
workflow.add_node("router", router_node)
workflow.add_node("researcher", run_researcher)
workflow.add_node("commander", run_commander)
workflow.add_node("mathematician", run_mathematician)
workflow.add_node("writer", writer_node)

# Point d'entrée
workflow.set_entry_point("router")

# Edges conditionnels depuis le routeur
workflow.add_conditional_edges(
    "router",
    lambda x: x["next_node"],
    {
        "researcher": "researcher",
        "commander": "commander",
        "mathematician": "mathematician",
        "writer": "writer"
    }
)

# Edges séquentiels vers le rédacteur
workflow.add_edge("researcher", "writer")
workflow.add_edge("commander", "writer")
workflow.add_edge("mathematician", "writer")
workflow.add_edge("writer", END)

# Compilation du système orchestré
sofia_multi_agent_system = workflow.compile()

def process_query(query: str):
    """Fonction principale pour invoquer le graphe."""
    inputs = {"messages": [HumanMessage(content=query)]}
    final_state = sofia_multi_agent_system.invoke(inputs, {"recursion_limit": 10})
    return final_state["messages"][-1].content
