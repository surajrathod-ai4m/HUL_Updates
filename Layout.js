import React from "react";
import Header from "./Header/Header";
import Footer from "./Footer/Footer";
 


function Layout({ children }) {
  return (
    <div style={{ display: "flex" }}>
     
      <div style={{ display: "flex", flexDirection: "column", flex: 1 }}>
        <Header/>
        <main style={{ flex: 1, padding: "20px" }}>{children}</main>
        <Footer/>
      </div>
    </div>
  );
}

export default Layout;