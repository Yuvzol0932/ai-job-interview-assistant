import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import type { InterviewState, Report } from "../types";

interface AppContextValue {
  resumeText: string;
  setResumeText: (text: string) => void;
  interviewState: InterviewState | null;
  setInterviewState: (state: InterviewState | null) => void;
  currentReport: Report | null;
  setCurrentReport: (report: Report | null) => void;
}

const AppContext = createContext<AppContextValue | null>(null);

function readSessionState<T>(key: string): T | null {
  try {
    const raw = sessionStorage.getItem(key);
    return raw ? (JSON.parse(raw) as T) : null;
  } catch {
    return null;
  }
}

export function AppProvider({ children }: { children: ReactNode }) {
  const [resumeText, setResumeText] = useState("");
  const [interviewState, setInterviewState] = useState<InterviewState | null>(
    () => readSessionState<InterviewState>("interview_state"),
  );
  const [currentReport, setCurrentReport] = useState<Report | null>(null);

  useEffect(() => {
    if (interviewState) {
      sessionStorage.setItem("interview_state", JSON.stringify(interviewState));
    } else {
      sessionStorage.removeItem("interview_state");
    }
  }, [interviewState]);

  return (
    <AppContext.Provider
      value={{
        resumeText,
        setResumeText,
        interviewState,
        setInterviewState,
        currentReport,
        setCurrentReport,
      }}
    >
      {children}
    </AppContext.Provider>
  );
}

export function useApp(): AppContextValue {
  const value = useContext(AppContext);
  if (!value) {
    throw new Error("useApp 必须在 AppProvider 内使用");
  }
  return value;
}
