'use client';

import { useState } from 'react';

export default function BitsRefPage() {

  const [file,setFile] = useState<File | null>(null)
  const [loading,setLoading] = useState(false)
  const [downloadUrl,setDownloadUrl] = useState("")

  const uploadPdf = async () => {

    if(!file){
      alert("Please upload PDF")
      return
    }

    setLoading(true)

    const formData = new FormData()
    formData.append("file",file)

    try{

      const res = await fetch(
        "http://localhost:8000/api/bits/upload",
        {
          method:"POST",
          body:formData
        }
      )

      const data = await res.json()

      setDownloadUrl(
        `http://localhost:8000/api/bits/download/${data.job_id}`
      )

    }catch(err){
      alert("Conversion failed")
    }

    setLoading(false)

  }

  return(

    <div style={styles.page}>

      <h2 style={styles.title}>
        BITS Reference Converter
      </h2>

      <p style={styles.subtitle}>
        Upload a PDF file and convert references into BITS XML format
      </p>

      <div style={styles.uploadBox}>

        <input
          type="file"
          accept="application/pdf"
          onChange={(e)=>setFile(e.target.files?.[0] || null)}
        />

        <br/><br/>

        <button
          style={styles.btn}
          onClick={uploadPdf}
          disabled={loading}
        >
          {loading ? "Processing..." : "Convert to XML"}
        </button>

      </div>

      {downloadUrl && (

        <div style={styles.downloadBox}>

          <p>✅ Conversion completed</p>

          <a
            href={downloadUrl}
            style={styles.downloadBtn}
          >
            Download XML
          </a>

          <p style={styles.note}>
            File will auto delete after 30 minutes
          </p>

        </div>

      )}

    </div>

  )

}

/* ================= STYLES ================= */

const styles:any = {

 page:{
  maxWidth:"900px",
  margin:"40px auto",
  padding:"40px",
  background:"#fff",
  borderRadius:"16px",
  boxShadow:"0 10px 30px rgba(0,0,0,0.08)"
 },

 title:{
  textAlign:"center",
  fontSize:"28px",
  marginBottom:"10px"
 },

 subtitle:{
  textAlign:"center",
  color:"#475569",
  marginBottom:"30px"
 },

 uploadBox:{
  border:"2px dashed #38bdf8",
  padding:"40px",
  borderRadius:"14px",
  textAlign:"center",
  background:"#f8fafc"
 },

 btn:{
  padding:"10px 20px",
  borderRadius:"10px",
  border:"none",
  background:"#38bdf8",
  color:"#fff",
  cursor:"pointer",
  fontWeight:"bold"
 },

 downloadBox:{
  marginTop:"30px",
  textAlign:"center"
 },

 downloadBtn:{
  display:"inline-block",
  marginTop:"10px",
  padding:"10px 18px",
  background:"#22c55e",
  color:"#fff",
  borderRadius:"8px",
  textDecoration:"none"
 },

 note:{
  marginTop:"10px",
  fontSize:"12px",
  color:"#64748b"
 }

}