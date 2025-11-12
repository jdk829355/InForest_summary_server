from langchain_community.document_loaders import WebBaseLoader
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.chains.summarize import load_summarize_chain
from langchain_text_splitters import RecursiveCharacterTextSplitter
import dotenv
from langchain_classic.prompts import PromptTemplate
from enum import Enum

dotenv.load_dotenv()

class TaskStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class SummaryGenerator:
    def __init__(self):
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", temperature=0)

        self.prompt_template = """
        아래는 문서에서 추출한 핵심 포인트들입니다.
        이 포인트들을 주제별로 묶어서 하나의 '상세한 보고서' 형식으로 한국어로 재구성해 주세요.

        정보를 생략하거나 요약하지 말고,
        아래 포인트들의 내용을 가능한 한 자세하게 포함시켜 주세요.
        
        --- 핵심 포인트 시작 ---
        {text}
        --- 핵심 포인트 끝 ---
        
        상세한 재구성 보고서 (마크다운 형식 권장):
        """
        self.prompt = PromptTemplate(template=self.prompt_template, input_variables=["text"])

        # --- (stuff 용 프롬프트는 주석 처리) ---
        # summary_prompt_template = (...)
        # self.summary_prompt = ...

        # --- 2. 체인 타입을 "stuff"로 변경 ---
        self.summary_chain = load_summarize_chain(
            llm,
            chain_type="stuff",
            # stuff에 필요한 프롬프트들을 전달합니다.
            prompt=self.prompt,
            verbose=True # 각 단계가 어떻게 실행되는지 보려면 True로 설정
        )

    def summarize(self, url, tree_id):
        loader = WebBaseLoader(url)
        documents = loader.load()
        result = self.summary_chain.invoke({"input_documents": documents})['output_text']
        return result

if __name__ == "__main__":
    url = "https://python.org"
    summarizer = SummaryGenerator()
    summary = summarizer.summarize(url, "test_tree_id")
    print("Summary:\n", summary)