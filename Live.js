import React, { useState, useEffect, useRef,useMemo } from "react";
import { Card, CardBody, CardTitle, Col, Row } from "reactstrap";
import "./CSS/Live.css";
import img_3d from "./Images/3dimg.png";
import Tank from "./Utils/tank";
import Horizontalsealing from "./Utils/Horizontalsealing";
import Laminate from "./Utils/Laminate";
import Pulling from "./Utils/Pulling";
import VerticleSealing from "./Utils/VerticleSealing";
import { fetchCount, fetchLiveCount } from "./API/Api";
//import SealingLeakageModal from "./Utils/SealingLeakageModal";

const Live = () => {
  const [isHopperModalOpen, setIsHopperModalOpen] = useState(false);
  const [isHorizontalSealingModalOpen, setIsHorizontalSealingModalOpen] = useState(false);
  const [isLaminateModalOpen, setIsLaminateModalOpen] = useState(false);
  const [isPullingModalOpen, setIsPullingModalOpen] = useState(false);
  const [isVerticleModalOpen, setIsVerticleModalOpen] = useState(false);
  const [verticlePressure, setVerticlePressure] = useState([]);
  const [verticleFrontTemp, setVerticleFrontTemp] = useState([]);
  const [verticleRearTemp, setVerticleRearTemp] = useState([]);
  const [verticleTime, setVerticleTime] = useState([]);
  const [horizontalPressure, setHorizontalPressure] = useState([]);
  const [horizonatlTime, setHorizonatlTime] = useState([]);
  const [horizonatlFrontTemp, setHorizonatlFrontTemp] = useState([]);
  const [horizonatlRearTemp, setHorizonatlRearTemp] = useState([]);
  const [hopperValue, setHopperValue] = useState("");
  const [laminateValue, setLaminateValue] = useState("");
  const [pullingValue, setPullingValue] = useState("");
  const [cardData, setCardData] = useState([0]);
  const [isSealingLeakageModalOpen, setIsSealingLeakageModalOpen] = useState(false);
  const modalOpenFlagRef = useRef(false);


  useEffect(() => {
    const fetchCardData = async () => {
      try {
        const data = await fetchCount();
        // console.log("Data", data.sealant_leakage.status)
        const mappedData = [
          {
            title: "Sealing Leakage",
            value:
              data.sealant_leakage.status !== null
                ? data.sealant_leakage.status
                : "--",
            color: data.sealant_leakage.color,
          },
          {
            title: "Laminate Pulling",
            value:
              data.laminate_pulling.status !== null
                ? data.laminate_pulling.status
                : "--",
            color: data.laminate_pulling.color,
          },
          {
            title: "Laminate Jamming",
            value:
              data.laminate_jamming.status !== null
                ? data.laminate_jamming.status
                : "--",
            color: data.laminate_jamming.color,
          },
        ];

        setCardData(mappedData);


        setHopperValue(data.hopper_level.value !== undefined ? data.hopper_level.value.toFixed(2) : "--");
        setLaminateValue(data.laminate_cof_variation.value !== undefined ? data.laminate_cof_variation.value.toFixed(2) : "--");
        setPullingValue(data.pulling_roller_current_variation.value !== undefined ? data.pulling_roller_current_variation.value.toFixed(2) : "--");
        if (!modalOpenFlagRef.current && data.sealant_leakage.status !== null && data.sealant_leakage.status !== "None") {
          setIsSealingLeakageModalOpen(true);
          modalOpenFlagRef.current = true;
          setTimeout(() => {
            setIsSealingLeakageModalOpen(false);
            modalOpenFlagRef.current = false;
          }, 3000);
        }

      } catch (error) {
        console.error("Error fetching card data:", error);
        setCardData([
          { title: "Sealing Leakage", value: "--" },
          { title: "Laminate Pulling", value: "--" },
          { title: "Laminate Jamming", value: "--" },
        ]);

      }
    };

    fetchCardData();

    const intervalId = setInterval(fetchCardData, 3000);

    return () => clearInterval(intervalId);
  }, []);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const liveResponse = await fetchLiveCount();
        // console.log("LIVE", liveResponse)
        setVerticlePressure(liveResponse.ver_sealer_pressure.value.toFixed(2));
        setHorizontalPressure(
          liveResponse.hor_sealer_pressure.value.toFixed(2)
        );
        //	const hozTimeInSeconds = (liveResponse.hoz_time.value / 1000).toFixed(2);
        setHorizonatlTime(liveResponse.hoz_time.value.toFixed(2));
        setVerticleTime(liveResponse.hoz_time.value.toFixed(2));
        setHorizonatlFrontTemp(liveResponse.hoz_front_temp.value.toFixed(2));
        setHorizonatlRearTemp(liveResponse.hoz_rear_temp.value.toFixed(2));
        setVerticleFrontTemp(liveResponse.ver_front_temp.value.toFixed(2));
        setVerticleRearTemp(liveResponse.ver_rear_temp.value.toFixed(2));
      } catch (error) {
        console.error("Error fetching card data:", error);
      }
    };

    fetchData();

    const intervalId = setInterval(fetchData, 5000);

    return () => clearInterval(intervalId);
  }, []);



  const dotsData = useMemo(
    () => [
      { left: "52%", top: "15%", color: "white", label: "1" },
      { left: "52%", top: "46%", color: "white", label: "2" },
      { left: "46%", top: "40%", color: "white", label: "3" },
      { left: "53%", top: "42%", color: "white", label: "4" },
      { left: "46.5%", top: "50%", color: "white", label: "5" },
    ],
    []
  );
  const handleCardClick = (label) => {
    if (label === "1") {
      setIsHopperModalOpen(true);
    }
    else if (label === "2") {
      setIsHorizontalSealingModalOpen(true)
    }
    else if (label === "4") {
      setIsLaminateModalOpen(true);
    } else if (label === "5") {
      setIsPullingModalOpen(true);
    } else if (label === "3") {
      setIsVerticleModalOpen(true);
    }
  };

  const renderCardBody = (value) => {
    return value !== null ? value : "--";
  };

  return (
    <div>
      <Row>
        <Col></Col>
        {cardData.map((card, index) => (
          <Col key={index}>
            <Card
              className={`card-style ${card.color === "#FF0000"
                ? "red-shade"
                : card.color === "#FFBF00"
                  ? "yellow-shade"
                  : ""
                }`}
            >
              <CardTitle className="mx-3   cardtitlefont">
                {card.title}
              </CardTitle>
              <CardBody className="cardbody-font" style={{ color: card.color }}>
                {renderCardBody(card.value)}
              </CardBody>
            </Card>
          </Col>
        ))}

        <Col></Col>
      </Row>
      {isSealingLeakageModalOpen && (
        <Row style={{ color: "white", textAlign: "center" }} >
          <h3 className="justify-content-center mt-3 position-fixed">
            {"Change Horizontal Stroke,Pressure to 5.2 kgf"}
          </h3>
        </Row>)}
      <Row className="mt-5">
        <Col className="d-flex mt-3 justify-content-center position-relative">
          <img
            src={img_3d}
            alt="img3d"
            className="img-size position-relative"
          />
          {dotsData.map((dot, index) => (
            <div
              key={index}
              className={`dot dot-${dot.label}`}
              style={{
                left: dot.left,
                top: dot.top,
                backgroundColor: dot.color,
              }}
            >
              <div className="line-arrow"></div>
              <Card
                className="card-at-end"
                onClick={() => handleCardClick(dot.label)}
              >
                <CardTitle className="mx-3 mt-1 cardtitlefont">
                  {dot.label === "1"
                    ? "Hopper Level"
                    : dot.label === "3"
                      ? "Verticle Sealers"
                      : dot.label === "2"
                        ? "Horizontal Sealer"
                        : dot.label === "4"
                          ? "Laminate COF Variation"
                          : dot.label === "5"
                            ? "Pulling Roller Current Variation"
                            : `Card ${dot.label}`}
                </CardTitle>
                <CardBody className="cardbody">
                  {dot.label === "1" ? (
                    <strong>{hopperValue}%</strong>
                  ) : dot.label === "3" ? (
                    <>
                      <div>
                        Pressure: <strong>{verticlePressure} kgf</strong>
                      </div>
                      <div>
                        Time: <strong>{verticleTime}ms</strong>
                      </div>
                      <div>
                        Front Temp: <strong>{verticleFrontTemp}°C</strong>{" "}
                      </div>
                      <div>
                        Rear Temp: <strong>{verticleRearTemp} °C</strong>{" "}
                      </div>
                    </>
                  ) : dot.label === "2" ? (
                    <>
                      <div>
                        Pressure: <strong>{horizontalPressure} kgf</strong>
                      </div>
                      <div>
                        Time: <strong>{horizonatlTime}ms</strong>
                      </div>
                      <div>
                        Front Temp: <strong>{horizonatlFrontTemp}°C</strong>
                      </div>
                      <div>
                        Rear Temp: <strong>{horizonatlRearTemp}°C</strong>
                      </div>
                    </>
                  ) : dot.label === "4" ? (
                    <strong>{laminateValue}%</strong>
                  ) : dot.label === "5" ? (
                    <strong>{pullingValue}%</strong>
                  ) : (
                    `Content for card ${dot.label}`
                  )}
                </CardBody>
              </Card>
            </div>
          ))}
        </Col>
      </Row>
      <Tank isOpen={isHopperModalOpen} toggle={() => setIsHopperModalOpen(false)} />
      <Laminate
        isOpen={isLaminateModalOpen}
        toggle={() => setIsLaminateModalOpen(false)}
      />
      <Pulling
        isOpen={isPullingModalOpen}
        toggle={() => setIsPullingModalOpen(false)}
      />
      <VerticleSealing
        isOpen={isVerticleModalOpen}
        toggle={() => setIsVerticleModalOpen(false)}
        time_value={verticleTime}
      />


      <Horizontalsealing
        isOpen={isHorizontalSealingModalOpen}
        toggle={() => setIsHorizontalSealingModalOpen(false)}
        time_value={horizonatlTime}
      />
      {/* <SealingLeakageModal
        isOpen={isSealingLeakageModalOpen}
        toggle={() => setIsSealingLeakageModalOpen(false)}
      />*/}




    </div>
  );
};

export default Live;