from collections import defaultdict
import re

categories = [
    "Customer Service",
    "Financial Performance",
    "Risk Management and Compliance",
    "Corporate Social Responsibility",
    "Leadership",
    "Technology"
]

# Example keywords for now to test
category_keywords = [
    ["support", "help", "assistance", "service", "satisfaction", "agent", "representative", "call center", "chat", "ticket", "resolution", "complaint", "response time", "issue", "escalation", "feedback", "rating", "survey", "interaction", "troubleshooting", "guidance", "consultation", "FAQ", "user-friendly", "onboarding", "policy", "customer-first", "follow-up", "loyalty", "experience", "queue", "chatbot", "automated response", "communication", "engagement", "retention", "handling", "quality", "care", "personalized", "resolution time", "empathy", "responsiveness", "courtesy", "professionalism", "availability", "convenience", "reliability", "assistance request", "inquiry", "seamless", "waiting time", "outreach", "relationship", "expectations", "helpful", "support desk", "CRM", "workflow", "real-time", "assistance level", "multichannel", "hotline", "call back", "voice support", "live chat", "24/7", "expertise", "dedicated", "satisfaction level", "experience improvement", "referral", "feedback loop", "complaints resolution", "service quality", "troubleshooting guide", "redressal", "dispute", "problem-solving", "knowledge base", "escalation matrix", "resolution tracking", "remote support", "promptness", "service-oriented", "product support", "service failure", "non-responsive", "tech support", "query handling", "post-sales", "proactive", "sentiment", "voice of customer", "grievances", "waiting period", "refund policy", "user-centric", "helpdesk", "digital support", "virtual assistant", "callback request", "communication gap", "follow-up process", "automated IVR", "seamless experience"],
    ["revenue", "profit", "earnings", "growth", "loss", "EBITDA", "net income", "margin", "cost", "expense", "financials", "cash flow", "balance sheet", "investment", "return", "forecast", "fiscal", "sales", "dividends", "assets", "liabilities", "capital", "depreciation", "equity", "valuation", "debt", "funding", "reserves", "ROI", "financial health", "liquidity", "P&L", "break-even", "turnover", "restructuring", "operating income", "gross profit", "stock price", "shareholder", "bond", "credit rating", "hedge", "cost reduction", "fiscal year", "economic outlook", "operating expenses", "capital expenditure", "retained earnings", "financial planning", "revenue stream", "monetization", "financial statement", "bottom line", "budget", "revenue model", "funding round", "M&A", "quarterly report", "annual report", "savings", "expenditures", "profitability", "investment strategy", "stock performance", "IPO", "solvency", "leverage", "return on assets", "working capital", "accounts receivable", "accounts payable", "financial analysis", "fiscal policy", "pricing strategy", "buyback", "dividend yield", "capital allocation", "interest rate", "tax", "treasury", "venture capital", "private equity", "fundraising", "due diligence", "valuation model", "restructuring costs", "breakeven analysis", "liquidity ratio", "financial projection", "analyst rating", "economic downturn", "fiscal deficit", "margin expansion", "economic indicators", "capital gains", "yield curve", "financial restructuring", "cost structure", "operating leverage", "tax benefits", "revenue diversification", "market capitalization"],
    ["compliance", "regulation", "audit", "fraud", "risk assessment", "security", "governance", "controls", "legal", "cybersecurity", "anti-money laundering", "data breach", "due diligence", "financial fraud", "internal controls", "regulatory framework", "compliance audit", "penalty", "ethics", "enforcement", "SOX compliance", "GDPR", "data privacy", "investigation", "legal risk", "oversight", "reporting", "risk appetite", "identity theft", "transparency", "whistleblower", "red flag", "sanction", "policy violation", "litigation", "breach of contract", "data security", "vulnerability", "regulatory compliance", "risk mitigation", "financial crime", "sanction screening", "monitoring", "suspicious activity", "policy adherence", "accountability", "confidentiality", "whistleblowing", "anti-bribery", "risk exposure", "financial stability", "third-party risk", "insurance", "regulatory landscape", "ethical standards", "asset protection", "data governance", "industry standards", "tax compliance", "operational risk", "policy enforcement", "legal framework", "anti-corruption", "protection", "control measures", "licensing", "trade compliance", "reporting obligations", "risk management framework", "money laundering", "framework adherence", "anti-fraud", "cybersecurity incident", "internal audit", "forensic analysis", "business continuity", "oversight committee", "compliance training", "breach detection", "case management", "penalty risk", "due diligence report", "contract risk", "cyber threat", "enterprise risk", "fraud prevention", "investigative audit", "consumer protection", "strategic risk", "vendor risk", "policy development", "ethics committee", "non-compliance", "incident response", "whistleblower protection", "credit risk", "financial regulations", "governance risk", "risk evaluation", "suspicious activity report", "legal dispute", "consumer rights", "corporate compliance"],
    ["sustainability", "ethics", "community", "green", "responsibility", "environmental impact", "philanthropy", "volunteerism", "eco-friendly", "CSR initiatives", "carbon footprint", "social impact", "fair trade", "ethical sourcing", "inclusivity", "workplace diversity", "charitable giving", "environmental sustainability", "circular economy", "energy efficiency", "responsible sourcing", "corporate citizenship", "transparency", "accountability", "environmental policy", "community service", "donations", "social responsibility", "impact investing", "sustainable business", "corporate giving", "emissions reduction", "governance", "workplace equality", "diversity and inclusion", "labor rights", "ethical leadership", "non-profit partnerships", "renewable energy", "fair wages", "social equity", "employee engagement", "pollution reduction", "ESG", "conservation", "humanitarian aid", "supply chain responsibility", "corporate philanthropy", "carbon neutrality", "fair labor", "corporate ethics", "biodiversity", "community engagement", "climate action", "sustainable finance", "disaster relief", "economic development", "stakeholder engagement", "animal welfare", "ethical business", "human rights", "impact measurement", "regulatory compliance", "corporate governance", "habitat protection", "water conservation", "sustainable sourcing", "ethical investment", "eco-conscious", "corporate volunteerism", "emissions control", "workplace safety", "net zero", "sustainability reporting", "social innovation", "waste management", "ethical standards", "ethical trade", "charity partnerships", "sustainable materials", "zero waste", "transparency report", "clean energy", "affordable housing", "responsible business", "renewable resources", "plastic reduction", "environmental awareness", "sustainability goals", "corporate culture", "advocacy", "public policy", "reducing inequality", "ethical hiring", "sustainable strategy", "green initiatives", "worker welfare", "corporate activism", "reducing waste", "fair supply chain", "corporate initiatives"],
    ["CEO", "management", "executive", "vision", "leadership", "board of directors", "decision-making", "strategy", "influence", "governance", "company culture", "innovation", "mission", "productivity", "team building", "motivation", "management style", "transparency", "ethical leadership", "communication", "hierarchy", "strategic thinking", "mentorship", "problem-solving", "delegation", "stakeholder management", "succession planning", "resilience", "operational excellence", "change management", "corporate strategy", "thought leadership", "trust", "reputation", "organizational development", "performance", "adaptability", "accountability", "empowerment", "inspiration", "business acumen", "executive presence", "agility", "coaching", "management training", "negotiation", "conflict resolution", "strategic goals", "emotional intelligence", "collaboration", "visionary", "goal setting", "persuasion", "executive leadership", "management effectiveness", "professional development", "adaptability", "board oversight", "corporate vision", "team dynamics", "organizational leadership", "people management", "personal branding", "reputation management", "strategic partnerships", "executive coaching", "situational leadership", "ethical decision-making", "work culture", "transformational leadership", "leadership pipeline", "innovation leadership", "high-performance teams", "productivity improvement", "critical thinking", "executive decisions", "strategic foresight", "risk-taking", "value-driven leadership", "organizational success", "empowering teams", "inclusive leadership", "communication skills", "workplace ethics", "sustainability leadership", "business leadership", "vision execution", "market leadership", "integrity", "succession planning", "stakeholder engagement", "performance management", "culture building", "visionary leadership", "risk leadership", "leadership impact"],
    ["innovation", "AI", "cloud", "software", "tech", "automation", "cybersecurity", "digital", "blockchain", "machine learning", "IoT", "data science", "big data", "analytics", "VR", "AR", "quantum computing", "robotics", "SaaS", "edge computing", "5G", "DevOps", "coding", "IT security", "cybersecurity threats", "API", "infrastructure", "microservices", "AI ethics", "tech stack", "enterprise software", "data center", "hybrid cloud", "cloud migration", "UX design", "digital transformation", "NoSQL", "cloud-native", "smart devices", "fintech", "digital banking", "NLP", "voice recognition", "chatbot", "cyber resilience", "cybersecurity policies", "AI governance", "data privacy", "AI-driven", "web3", "software testing", "IoT devices", "machine vision", "CI/CD", "software architecture", "programming languages", "digital infrastructure", "virtual assistant", "productivity tools", "smart cities", "IT automation", "deep learning", "computer vision", "metaverse", "cloud computing", "DevSecOps", "software development", "quantum algorithms", "secure coding", "IT governance", "app development", "tech regulations", "IT strategy", "digital security", "IT compliance", "data warehousing", "VR training", "artificial intelligence", "tech adoption", "serverless computing", "tech ethics", "cybersecurity threats", "smart contracts", "containerization", "autonomous systems", "cloud security"]
]

inverted_keyword_cats = {}

for i in range(len(categories)):
    cat = categories[i]
    vals = category_keywords[i]
    for v in vals:
        if v in inverted_keyword_cats:
            inverted_keyword_cats[v].append(i)
        else:
            inverted_keyword_cats[v] = [i]


def generate_keywords(text):
    # Scan text for our keywords
    # Count occurrences of each keyword
    # Store keyword to its category
    # Return category and keyword details
    
    # Parameters:
    #   text: str, input paragraph to analyze
    #   category_keywords: dict, mapping of category names to lists of keywords
        
    # Returns:
    #   dict, mapping of category names to keyword occurrence counts and keywords found
    
    # Normalizing text
    text = text.lower()
    words = [w.strip().lower() for w in text.split(' ')]

    # Mapping of category names to keyword occurrence counts
    keyword_details = defaultdict(lambda: {"count": 0, "keywords": set()})

    # Find key phrases of word count 1, 2, and 3
    for w_cnt in range(3):
        words_comb = [' '.join(words[j:j+w_cnt]) for j in range(len(words) - w_cnt)] if w_cnt > 0 else words

        for phrase in words_comb: # Iterating over phrases in article
            if phrase not in inverted_keyword_cats:  # phrase has no matching category
                continue
            for i in inverted_keyword_cats[phrase]:  # add matching categories to result
                keyword_details[categories[i]]["keywords"].add(phrase)

    # clean up
    for category in keyword_details.keys():
        if len(keyword_details[category]["keywords"]) == 0:
            del keyword_details[category]  # remove absent category
        else:
            keyword_details[category]["count"] = len(keyword_details[category]["keywords"])  # record keyword count
            keyword_details[category]["keywords"] = list(keyword_details[category]["keywords"])  # change keyword set to array

    return dict(keyword_details)


def generate_keywords_sorted(text):
    """
    Wrapper around generate_keywords to sort categories by the number of mentions (count).
    """
    # Get the keyword details using the existing function
    keyword_details = generate_keywords(text)
    
    # Sort the categories by the count of mentions in descending order
    sorted_keyword_details = dict(
        sorted(keyword_details.items(), key=lambda item: item[1]["count"], reverse=True)
    )

    return sorted_keyword_details


if __name__ == "__main__":
    # Sample article
    # Webster eyes $100B threshold, invests in hiring and tech 
    # https://finance.yahoo.com/news/webster-eyes-100b-threshold-invests-102036948.html
    sample_article = "Webster eyes $100B threshold, invests in hiring and tech - As Webster Bank marches toward the $100 billion-asset threshold that would make it a Category IV bank, the lender is stepping up its hiring efforts and fortifying its cybersecurity infrastructure. To prepare for crossing that line, the Stamford, Connecticut-based regional bank – which now counts about $80 billion in assets – is investing to bolster its risk and compliance infrastructure, and readying for higher capital and liquidity requirements, as well as more regulatory reporting. The bank is also approaching the milepost with cybersecurity top of mind, since the Category IV designation heightens expectations around the use and collection of data, said Vikram Nafde, the bank’s chief information officer. “What we have to do for that is a series of things in the space of data, cybersecurity, but also digital and the regulatory reporting,” Nafde said during a recent interview. “There’s a big component of technology … as we get closer and closer to the $100 billion mark.” To that end, the bank is hiring with an eye toward strengthening its risk framework and controls, Nafde said. Webster will also hire for new data-related roles, including those concerning data collection, storing and governance, and continues hiring for cybersecurity roles, he said. The bank, which has close to 4,300 employees, plans to hire about 200 people this year. Of that number, about 25 will be hired for technology and cybersecurity roles on the IT team, said Nafde, who’s been at the bank since 2020 and became CIO in 2022. Although there’s chatter that the $100 billion barrier may go away, given calls for tailoring and expectations of regulatory relaxation under the Trump administration, Webster CEO John Ciulla said during a March 5 conference appearance “that’s not our base case [although] it might get less onerous.” Still, the possibility of change has led the bank to be thoughtful in building out its capabilities, executives indicated. About three-quarters of Webster’s Category IV-related expenses shareholders “would want us to do anyway, to build a more resilient and more industrialized bank,” Ciulla said. The other 25% “are a little bit regulatory check-the-box,” so the bank is trying to stagger those expenses, so that if the $100 billion barrier goes away or the requirements for becoming a large bank change, Webster can defer some of those expenses, he said. As it becomes Category IV-ready, the bank expects to add between $40 million and $60 million in run rate operating expenses over the next several years, Webster CFO Neal Holland said during the bank’s most recent earnings call. The lender expects 2025 expenses to total around $1.4 billion, and Nafde said the bank’s tech spending will be higher this year than last. As the bank beefs up to accommodate growth, cybersecurity remains a top priority across the business, Nafde said. Webster maintains a “defense in-depth” strategy to ward off threats, assuming a breach posture rather than simply relying on prevention measures. Increasingly, the bank is applying zero-trust principles – referring to a security strategy that focuses on strict controls and continuous authentication – and zeroing in on data loss prevention, to keep sensitive information from being leaked, he said. “We have various tools layered in to make sure we have the right cyber posture,” Nafde said. Patty Voight, Webster’s chief information security officer, said the bank also engages in ongoing awareness and training with colleagues, customers and third-party vendors Webster works with. As the bank constantly assesses its third- and fourth-party ties, it considers what kind of information is stored with them, and employs rigorous protocols with new partnerships, Nafde said. “Because risk is out there, a passive approach is not going to work,” he said. Investments the bank is making for its Category IV move put it in a “position of optionality,” Ciulla said. If mergers and acquisitions become easier from a regulatory standpoint, the bank will be ready with the right technology, risk and data infrastructure for a whole-bank acquisition in a year, or two or three, he said. For now, Webster is focused on tuck-in acquisitions that can strengthen the bank’s deposit and fee franchise. The bank’s last deal was its 2023 purchase of Ametros, a custodian and administrator of medical funds from insurance claim settlements. Webster is interested in businesses that would further enhance its healthcare vertical, Ciulla said last week. The lender’s move to the cloud makes acquisitions far easier to integrate, Nafde noted. The bank is “essentially done” with that migration, having transitioned every business application to the cloud, and is in the process of shutting down data centers, he said. Being able to do M&A more nimbly is one of the perks of that move, he added. “The longest pole in the tent used to be, how can we get the data centers to connect and all the systems to work?” Nafde said, but today “lots of these smaller companies grew up in the cloud age.”"

    for i in range(1000):
    # Run function
        result = generate_keywords_sorted(sample_article) # Passing (article, categories + keywords)
    print(result)
    # pass
