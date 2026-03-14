'use client';

import { useRouter } from 'next/navigation';

export default function HeadTailPage() {

  const router = useRouter();

  const tools = [
    {
      name: "Head",
      desc: "Process and tag reference head section",
      path: "/Tools/xml-ref/head-tail/head"
    },
    {
      name: "Tail",
      desc: "Process and tag reference tail section",
      path: "/Tools/xml-ref/head-tail/tail"
    }
  ];

  return (
    <div style={styles.page}>

      <h2 style={styles.title}>Head & Tail Processing</h2>

      <p style={styles.subtitle}>
        Choose which part of the reference you want to process
      </p>

      <div style={styles.cardGrid}>

        {tools.map((tool, i) => (

          <div
            key={i}
            style={styles.toolCard}
            onClick={() => router.push(tool.path)}
          >

            <h3 style={styles.cardTitle}>
              {tool.name}
            </h3>

            <p style={styles.cardDesc}>
              {tool.desc}
            </p>

            <button style={styles.openBtn}>
              Open Tool
            </button>

          </div>

        ))}

      </div>

    </div>
  );
}

/* ================= STYLES ================= */

const styles:any = {

  page:{
    maxWidth:"1200px",
    margin:"40px auto",
    padding:"40px",
    background:"#ffffff",
    borderRadius:"16px",
    boxShadow:"0 10px 30px rgba(0,0,0,0.08)"
  },

  title:{
    textAlign:"center",
    fontSize:"30px",
    marginBottom:"10px",
    color:"#020617",
    fontWeight:600
  },

  subtitle:{
    textAlign:"center",
    color:"#475569",
    marginBottom:"40px",
    fontSize:"15px"
  },

  cardGrid:{
    display:"grid",
    gridTemplateColumns:"repeat(auto-fit,minmax(240px,1fr))",
    gap:"25px"
  },

  toolCard:{
    background:"#f8fafc",
    padding:"30px",
    borderRadius:"16px",
    border:"1px solid #e2e8f0",
    cursor:"pointer",
    transition:"all 0.2s ease",
    textAlign:"center"
  },

  cardTitle:{
    fontSize:"20px",
    fontWeight:600,
    marginBottom:"10px",
    color:"#0f172a"
  },

  cardDesc:{
    fontSize:"14px",
    color:"#475569",
    marginBottom:"20px"
  },

  openBtn:{
    background:"#38bdf8",
    border:"none",
    color:"#fff",
    padding:"10px 18px",
    borderRadius:"10px",
    cursor:"pointer",
    fontWeight:"bold"
  }

};