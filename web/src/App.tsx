import { HashRouter, Route, Routes } from "react-router-dom";
import { Layout } from "./components/Layout";
import { Home } from "./pages/Home";
import { Interview } from "./pages/Interview";
import { Jobs } from "./pages/Jobs";
import { ResumeDiagnosis } from "./pages/ResumeDiagnosis";
import { Review } from "./pages/Review";
import { AppProvider } from "./state/AppContext";

export default function App() {
  return (
    <AppProvider>
      <HashRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <Routes>
          <Route element={<Layout />}>
            <Route index element={<Home />} />
            <Route path="/resume" element={<ResumeDiagnosis />} />
            <Route path="/jobs" element={<Jobs />} />
            <Route path="/interview" element={<Interview />} />
            <Route path="/review" element={<Review />} />
            <Route path="*" element={<Home />} />
          </Route>
        </Routes>
      </HashRouter>
    </AppProvider>
  );
}
