import "../css/index.css";
import { NProgressContainer } from "~/vendor/nprogress";
import "~/vendor/fa";

function App({ Component, pageProps }) {
  return (
    <div className="App">
      <Component {...pageProps} />
      <NProgressContainer spinner={false} />
    </div>
  );
}

export default App;
