import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.svm import SVR
import plotly
import json

class Hotspot:
	def __init__(self, ):
		self.covid19api = 'https://api.covid19india.org/csv/latest/districts.csv'
		self.lat_long = pd.read_csv('data/lat_long.csv')
		self.lat_long.index = self.lat_long['district']
		df = pd.read_csv(self.covid19api)
		STATE = 'Maharashtra'		## Sticking with MH only
		self.districts = df[df.State==STATE].District.unique().tolist()
		try:
			self.districts.remove('Unknown')
		except:
			pass
		try:
			self.districts.remove('Other State')
		except:
			pass
		df = pd.pivot_table(df, index=['State', 'District', 'Date'])
		self.state = df.xs(STATE).copy(deep=True)

	def model(self, ):
		ela_pipeline = Pipeline(steps=[('scaler', StandardScaler()),
                            ('estimator', SVR(kernel='poly', degree=2, C=100, epsilon=0.001, coef0=10))])
		return ela_pipeline

	def predict(self,):
		X_predicted = {}
		for district in self.districts:
			X = self.state.xs(district)-self.state.xs(district).shift(1)
			X = pd.DataFrame(X.rolling(window=7).mean())
			X[X<0] = -X[X<0]
			X['lag_1'] = X.Confirmed.shift(1)
			X['lag_2'] = X.Confirmed.shift(2)
			X = X[['Confirmed', 'lag_1', 'lag_2']]
			X = X.fillna(0)
			y = X.Confirmed.shift(-1)
			ela_pipeline = self.model()
			ela_pipeline.fit(X[:-1].values, y[:-1])

			X_tt = []
			X_tt.append(ela_pipeline.predict(X[-1:])[0])
			X_tt.append(ela_pipeline.predict(np.hstack((X_tt[-1],X.Confirmed[-1:],X.Confirmed[-2:-1])).reshape(1,-1))[0])
			X_tt.append(ela_pipeline.predict(np.hstack((X_tt[-1],X_tt[-2],X.Confirmed[-1:])).reshape(1,-1))[0])
			for i in range(4):
				X_tt.append(ela_pipeline.predict(np.hstack((X_tt[-1],X_tt[-2],X.Confirmed[-1])).reshape(1,-1))[0])

			X_predicted[district] = [int(sum(X_tt)/len(X_tt)>X.Confirmed[-1]), int(sum(X_tt))]

		return X_predicted

	def join_latlong(self, X_predicted):
		waaw = pd.DataFrame(X_predicted).T
		waaw = waaw.join(self.lat_long)

		return waaw

	def get_map(self, waaw, js):
		# Create the figure and feed it all the prepared columns
		fig = go.Figure()

		fig.add_trace(go.Scattermapbox(
				lat=waaw['lat'],
				lon=waaw['lon'],
				mode='markers',
				marker=go.scattermapbox.Marker(
					sizemin=20,
					size=(waaw[0]*waaw[1])/4,
					color=waaw[0],
					cmin=0,
					cmax=1,
					colorscale=[[0, "#12c2e9"],
								[0.5, "#12c2e9"],
								[0.5, "#f64f59"],
								[1, "#f64f59"]],
					showscale=False,
					cauto=False,),
					customdata=waaw,
					hovertemplate='<extra></extra>' + 
							  '<em>%{customdata[2]}</em><br>' + 
							  '🚨  %{customdata[1]}<br>',
				),
		)

		# Specify layout information
		fig.update_layout(
			mapbox=dict(
				accesstoken='pk.eyJ1IjoiZW5yaWNvamFjb2JzIiwiYSI6ImNrcXN5cTR0MjBvM2cyb28zdzF5dnM2bG8ifQ.H55kEL_vM4bTRLhS3CdytQ', #
				center=go.layout.mapbox.Center(lat=19.663280, lon=75.300293),
				zoom=6,
			),
			margin=dict(t=10, b=10, r=10, l=10)
		)

		if js:
			return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
		else:
			return fig

	def find(self, js=True):
		X_predicted = self.predict()
		waaw = self.join_latlong(X_predicted)
		map = self.get_map(waaw, js=js)
		return map

if __name__ == '__main__':
	hotspot = Hotspot()
	hotspot.find(js=False).show()